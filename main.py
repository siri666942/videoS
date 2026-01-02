from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import os
import shutil
import tempfile
import asyncio
from pathlib import Path

from video_search_tool import VideoSearchTool
from configuration import video_config
from content_generator import ContentGenerator
from master_agent import MasterAgent
from certificate_generator import CertificateGenerator
from pydantic import BaseModel
import json

app = FastAPI(title="VedioS - 视频检索API", description="基于FastAPI的视频上传和检索服务")

# 添加CORS中间件，允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有头部
)

# 全局工具实例
video_tool = VideoSearchTool()
content_generator = ContentGenerator()
master_agent = MasterAgent()
certificate_generator = CertificateGenerator()

# 确保上传目录存在
UPLOAD_DIR = Path("uploaded_videos")
UPLOAD_DIR.mkdir(exist_ok=True)

# 内容存储目录
CONTENT_DIR = Path("generated_content")
CONTENT_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "VedioS 视频检索API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "上传视频文件并自动处理索引",
            "GET /search": "基于自然语言查询检索视频片段",
            "GET /video/{filename}": "获取上传的视频文件",
            "GET /index-info": "获取索引信息",
            "POST /extract-segment": "提取视频片段"
        }
    }

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    chunk_duration: float = Query(30.0, description="分块持续时间（秒）"),
    language: Optional[str] = Query(None, description="转录语言（可选，自动检测）")
):
    """
    上传视频文件，自动处理并建立索引

    - **file**: 视频文件（支持mp4、avi、mov等格式）
    - **chunk_duration**: 每个文本块的持续时间（秒）
    - **language**: 转录语言代码（可选）
    """
    # 验证文件类型
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式：{', '.join(allowed_extensions)}"
        )

    # 保存上传的文件
    temp_file_path = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # 验证文件大小（限制为500MB）
        file_size = os.path.getsize(temp_file_path)
        if file_size > 500 * 1024 * 1024:  # 500MB
            raise HTTPException(status_code=413, detail="文件过大，最大支持500MB")

        # 移动到上传目录
        final_filename = f"{file.filename}"
        final_path = UPLOAD_DIR / final_filename
        counter = 1
        while final_path.exists():
            name_without_ext = Path(file.filename).stem
            final_filename = f"{name_without_ext}_{counter}{file_extension}"
            final_path = UPLOAD_DIR / final_filename
            counter += 1

        shutil.move(temp_file_path, final_path)
        temp_file_path = None

        # 开始处理视频
        print(f"开始处理视频: {final_path}")
        result = await video_tool.index_video(
            str(final_path),
            chunk_duration=chunk_duration,
            language=language
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": "视频上传并索引成功",
                "data": {
                    "filename": final_filename,
                    "file_path": str(final_path),
                    "file_size": file_size,
                    "indexing_result": result
                }
            },
            status_code=200
        )

    except Exception as e:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"处理视频时出错: {str(e)}")
    finally:
        await file.close()

@app.get("/search")
async def search_videos(
    q: str = Query(..., description="自然语言查询"),
    top_k: int = Query(5, description="返回结果数量", ge=1, le=20),
    video_filename: str = Query(..., description="视频文件名")
):
    """
    基于自然语言查询检索相关视频片段

    - **q**: 查询文本
    - **top_k**: 返回的匹配结果数量
    - **video_filename**: 要检索的视频文件名
    """
    try:
        results = await video_tool.search_videos(q, top_k=top_k, video_filename=video_filename)

        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_result = {
                "score": result["score"],
                "text": result["text"],
                "start_time": result["start_time"],
                "end_time": result["end_time"],
                "duration": result["end_time"] - result["start_time"],
                "video_filename": Path(result["video_path"]).name,
                "chunk_index": result["chunk_index"]
            }
            formatted_results.append(formatted_result)

        return JSONResponse(
            content={
                "status": "success",
                "query": q,
                "total_results": len(formatted_results),
                "results": formatted_results
            },
            status_code=200
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索时出错: {str(e)}")

@app.get("/index-info")
async def get_index_info():
    """获取当前索引的统计信息"""
    try:
        info = video_tool.get_index_info()
        return JSONResponse(
            content={
                "status": "success",
                "index_info": info
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取索引信息时出错: {str(e)}")

@app.get("/video/{video_filename}")
async def get_video(video_filename: str):
    """
    获取上传的视频文件

    - **video_filename**: 视频文件名
    """
    video_path = UPLOAD_DIR / video_filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return FileResponse(
        path=str(video_path),
        media_type='video/mp4',
        filename=video_filename
    )

@app.post("/extract-segment")
async def extract_segment(
    video_path: str = Form(..., description="视频文件路径"),
    start_time: float = Form(..., description="开始时间（秒）", ge=0),
    end_time: float = Form(..., description="结束时间（秒）", ge=0),
    output_filename: str = Form(..., description="输出文件名")
):
    """
    提取视频片段

    - **video_path**: 源视频文件路径
    - **start_time**: 开始时间（秒）
    - **end_time**: 结束时间（秒）
    - **output_filename**: 输出文件名
    """
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="开始时间必须小于结束时间")

    # 检查视频文件是否存在，如果不是绝对路径则在上传目录中查找
    if not os.path.exists(video_path):
        # 尝试在uploaded_videos目录中查找
        potential_path = UPLOAD_DIR / video_path
        if os.path.exists(str(potential_path)):
            video_path = str(potential_path)
        else:
            # 再次尝试，如果video_path只包含文件名
            filename_only = Path(video_path).name
            potential_path = UPLOAD_DIR / filename_only
            if os.path.exists(str(potential_path)):
                video_path = str(potential_path)
            else:
                raise HTTPException(status_code=404, detail=f"视频文件不存在: {video_path} (尝试过: {potential_path})")

    # 确保输出目录存在
    output_dir = Path("extracted_segments")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_filename

    try:
        video_tool.extract_segment(video_path, start_time, end_time, str(output_path))

        # 验证输出文件是否成功创建
        if not os.path.exists(str(output_path)):
            raise HTTPException(status_code=500, detail="输出文件未能成功创建")

        return JSONResponse(
            content={
                "status": "success",
                "message": "视频片段提取成功",
                "data": {
                    "input_video": video_path,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "output_path": str(output_path),
                    "output_filename": output_filename
                }
            },
            status_code=200
        )

    except Exception as e:
        # 清理可能创建的输出文件
        if os.path.exists(str(output_path)):
            try:
                os.remove(str(output_path))
            except:
                pass
        raise HTTPException(status_code=500, detail=f"提取片段时出错: {str(e)}")

# ========== 新增API端点 ==========

class GenerateContentRequest(BaseModel):
    video_filename: str

class QuizSubmission(BaseModel):
    video_filename: str
    answers: List[Dict[str, Any]]  # [{"question_id": 1, "selected_answer": 0}, ...]
    user_name: Optional[str] = "学习者"

class MasterChatRequest(BaseModel):
    video_filename: str
    user_message: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

@app.post("/generate-content")
async def generate_content(request: GenerateContentRequest):
    """
    并行生成功能1+2、3、5的内容（标题+概要、思维导图、习题）
    """
    video_filename = request.video_filename
    try:
        # 检查内容是否已生成
        content_file = CONTENT_DIR / f"{Path(video_filename).stem}_content.json"
        if content_file.exists():
            with open(content_file, 'r', encoding='utf-8') as f:
                cached_content = json.load(f)
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "使用缓存内容",
                    "data": cached_content
                },
                status_code=200
            )
        
        # 并行生成内容（在实际实现中应该使用asyncio.gather）
        # 这里为了简化，先串行执行
        title_summary = content_generator.generate_title_and_summary(
            content_generator.transcript_storage.get_full_text(video_filename) or ""
        )
        mindmap = content_generator.generate_mindmap(
            content_generator.transcript_storage.get_full_text(video_filename) or ""
        )
        quiz = content_generator.generate_quiz(
            content_generator.transcript_storage.get_full_text(video_filename) or ""
        )
        
        content_data = {
            "title": title_summary.get("real_title", ""),
            "summary": title_summary.get("summary", ""),
            "mindmap": mindmap,
            "quiz": quiz
        }
        
        # 保存生成的内容
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "内容生成成功",
                "data": content_data
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成内容时出错: {str(e)}")

@app.get("/content/{video_filename}")
async def get_content(video_filename: str):
    """
    获取已生成的内容
    """
    try:
        content_file = CONTENT_DIR / f"{Path(video_filename).stem}_content.json"
        if not content_file.exists():
            raise HTTPException(status_code=404, detail="内容尚未生成，请先调用 /generate-content")
        
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
        
        return JSONResponse(
            content={
                "status": "success",
                "data": content_data
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内容时出错: {str(e)}")

@app.post("/submit-quiz")
async def submit_quiz(submission: QuizSubmission):
    """
    提交答题结果，返回评分和星级
    """
    try:
        # 获取习题内容
        content_file = CONTENT_DIR / f"{Path(submission.video_filename).stem}_content.json"
        if not content_file.exists():
            raise HTTPException(status_code=404, detail="习题尚未生成")
        
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
        
        quiz = content_data.get("quiz", {})
        questions = quiz.get("questions", [])
        
        if not questions:
            raise HTTPException(status_code=400, detail="没有可用的习题")
        
        # 计算得分
        correct_count = 0
        wrong_questions = []
        total = len(questions)
        
        for answer in submission.answers:
            question_id = answer.get("question_id")
            selected = answer.get("selected_answer")
            
            # 找到对应的问题
            question = next((q for q in questions if q.get("id") == question_id), None)
            if question:
                if selected == question.get("correct_answer"):
                    correct_count += 1
                else:
                    wrong_questions.append({
                        "id": question_id,
                        "question": question.get("question", ""),
                        "selected": selected,
                        "correct": question.get("correct_answer"),
                        "explanation": question.get("explanation", "")
                    })
        
        score = correct_count
        percentage = (score / total * 100) if total > 0 else 0
        
        # 计算星级（1-5星）
        if percentage >= 90:
            stars = 5
        elif percentage >= 80:
            stars = 4
        elif percentage >= 70:
            stars = 3
        elif percentage >= 60:
            stars = 2
        else:
            stars = 1
        
        # 保存答题结果
        quiz_result = {
            "video_filename": submission.video_filename,
            "user_name": submission.user_name,
            "score": score,
            "total": total,
            "percentage": percentage,
            "stars": stars,
            "wrong_questions": wrong_questions,
            "timestamp": str(Path(submission.video_filename).stem)
        }
        
        result_file = CONTENT_DIR / f"{Path(submission.video_filename).stem}_quiz_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(quiz_result, f, ensure_ascii=False, indent=2)
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "答题提交成功",
                "data": quiz_result
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交答题时出错: {str(e)}")

@app.post("/generate-certificate")
async def generate_certificate(
    video_filename: str = Form(...),
    user_name: str = Form(...),
    score: int = Form(...),
    total: int = Form(...)
):
    """
    生成毕业证书
    """
    try:
        # 获取视频标题
        content_file = CONTENT_DIR / f"{Path(video_filename).stem}_content.json"
        video_title = "视频课程"
        if content_file.exists():
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
                video_title = content_data.get("title", video_title)
        
        # 生成证书
        certificate_path = certificate_generator.generate_certificate(
            user_name=user_name,
            video_title=video_title,
            score=score,
            total=total
        )
        
        # 返回证书URL
        certificate_filename = Path(certificate_path).name
        certificate_url = f"/certificate/{certificate_filename}"
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "证书生成成功",
                "data": {
                    "certificate_url": certificate_url,
                    "certificate_path": certificate_path,
                    "certificate_filename": certificate_filename
                }
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成证书时出错: {str(e)}")

@app.get("/certificate/{certificate_filename}")
async def get_certificate(certificate_filename: str):
    """
    获取生成的证书图片
    """
    certificate_path = certificate_generator.output_dir / certificate_filename
    if not certificate_path.exists():
        raise HTTPException(status_code=404, detail="证书文件不存在")
    
    return FileResponse(
        path=str(certificate_path),
        media_type='image/png',
        filename=certificate_filename
    )

@app.post("/master-agent/identity")
async def generate_master_identity(video_filename: str = Query(...)):
    """
    生成大师身份
    """
    try:
        # 获取摘要
        content_file = CONTENT_DIR / f"{Path(video_filename).stem}_content.json"
        if not content_file.exists():
            raise HTTPException(status_code=404, detail="内容尚未生成")
        
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
        
        summary = content_data.get("summary", "")
        if not summary:
            raise HTTPException(status_code=400, detail="摘要不存在")
        
        identity = master_agent.generate_master_identity(summary)
        
        return JSONResponse(
            content={
                "status": "success",
                "data": identity
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成大师身份时出错: {str(e)}")

@app.post("/test/setup-demo-data")
async def setup_demo_data():
    """
    设置演示数据，用于快速测试功能（思维导图、习题等）
    """
    try:
        # 使用现有的内容数据
        demo_filename = "videoS_Instance_3.mp4"
        content_file = CONTENT_DIR / f"{Path(demo_filename).stem}_content.json"

        if not content_file.exists():
            raise HTTPException(status_code=404, detail="没有找到现有的演示数据")

        # 读取现有内容
        with open(content_file, 'r', encoding='utf-8') as f:
            demo_content = json.load(f)

        return JSONResponse(
            content={
                "status": "success",
                "message": "演示数据加载成功",
                "data": {
                    "video_filename": demo_filename,
                    "content": demo_content
                }
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置演示数据时出错: {str(e)}")

@app.post("/master-agent/chat")
async def chat_with_master(request: MasterChatRequest, stream: bool = Query(True, description="是否使用流式响应")):
    """
    与大师对话（支持流式响应）
    """
    try:
        # 获取摘要和答题结果
        content_file = CONTENT_DIR / f"{Path(request.video_filename).stem}_content.json"
        if not content_file.exists():
            raise HTTPException(status_code=404, detail="内容尚未生成")
        
        with open(content_file, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
        
        summary = content_data.get("summary", "")
        
        # 获取答题结果（如果存在）
        quiz_result_file = CONTENT_DIR / f"{Path(request.video_filename).stem}_quiz_result.json"
        quiz_results = None
        if quiz_result_file.exists():
            with open(quiz_result_file, 'r', encoding='utf-8') as f:
                quiz_results = json.load(f)
        
        # 与大师对话
        response = master_agent.chat_with_master(
            user_message=request.user_message,
            summary=summary,
            quiz_results=quiz_results,
            conversation_history=request.conversation_history,
            stream=stream
        )
        
        if stream:
            # 流式响应
            async def generate_stream():
                try:
                    for chunk in response:
                        # 发送SSE格式的数据
                        yield f"data: {json.dumps({'chunk': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                        # 强制刷新缓冲区，避免连接重置
                        await asyncio.sleep(0.01)
                    # 发送完成信号
                    yield f"data: {json.dumps({'chunk': '', 'done': True, 'master_info': master_agent.get_master_info()}, ensure_ascii=False)}\n\n"
                except ConnectionResetError:
                    # 客户端断开连接，静默处理
                    print("客户端断开连接，停止流式响应")
                    return
                except Exception as e:
                    error_msg = f"流式响应错误: {str(e)}"
                    try:
                        yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
                    except:
                        # 如果连错误信息都无法发送，静默处理
                        print(f"无法发送错误信息: {error_msg}")
                        return

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 非流式响应
            return JSONResponse(
                content={
                    "status": "success",
                    "data": {
                        "response": response,
                        "master_info": master_agent.get_master_info()
                    }
                },
                status_code=200
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话时出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8567)
