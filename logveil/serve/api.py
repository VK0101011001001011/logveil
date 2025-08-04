"""
LogVeil FastAPI Server
REST API for log sanitization with multi-format support and audit trails.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import tempfile
import json
import uuid
from pathlib import Path
from datetime import datetime

from core.redactor import RedactionEngine, RedactionTrace
from core.profiles import ProfileManager


# Pydantic models for API requests/responses
class SanitizeTextRequest(BaseModel):
    """Request model for text sanitization."""
    text: str = Field(..., description="Text content to sanitize")
    profile: Optional[str] = Field(None, description="Redaction profile to use")
    entropy_threshold: Optional[float] = Field(4.2, description="Entropy threshold for secret detection")
    enable_entropy: bool = Field(True, description="Enable entropy-based detection")
    trace: bool = Field(False, description="Generate redaction trace")


class SanitizeTextResponse(BaseModel):
    """Response model for text sanitization."""
    sanitized_text: str = Field(..., description="Sanitized text content")
    redaction_count: int = Field(..., description="Number of redactions performed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    trace: Optional[List[Dict[str, Any]]] = Field(None, description="Redaction trace if requested")


class ProfileInfo(BaseModel):
    """Model for profile information."""
    name: str
    description: str
    log_format: str
    pattern_count: int
    key_path_count: int


class EngineStatus(BaseModel):
    """Model for engine status information."""
    engine: str
    available: bool
    version: Optional[str]
    performance_score: int


class ServerStats(BaseModel):
    """Model for server statistics."""
    requests_processed: int
    total_redactions: int
    uptime_seconds: float
    available_profiles: List[str]
    active_engine: str


def create_app(redaction_engine: RedactionEngine, profile_manager: ProfileManager) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="LogVeil API",
        description="🔥 Production-grade log sanitization API with intelligent redaction",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Server state tracking
    server_stats = {
        "requests_processed": 0,
        "total_redactions": 0,
        "start_time": datetime.now(),
        "sessions": {}
    }
    
    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "LogVeil API",
            "version": "2.0.0",
            "description": "🔥 The Last Log Redactor You'll Ever Need",
            "endpoints": {
                "health": "/health",
                "sanitize_text": "/sanitize/text",
                "sanitize_file": "/sanitize/file",
                "profiles": "/profiles",
                "status": "/status"
            }
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "engine_available": True
        }
    
    @app.post("/sanitize/text", 
              response_model=SanitizeTextResponse,
              tags=["Sanitization"],
              summary="Sanitize text content",
              description="Sanitize raw text content with optional profile and tracing")
    async def sanitize_text(request: SanitizeTextRequest):
        """Sanitize text content."""
        try:
            start_time = datetime.now()
            
            # Configure engine based on request
            engine = RedactionEngine()
            engine.configure({
                'entropy_threshold': request.entropy_threshold,
                'enable_entropy_detection': request.enable_entropy,
                'trace_enabled': request.trace
            })
            
            # Load profile if specified
            if request.profile:
                profile = profile_manager.get_profile(request.profile)
                if not profile:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Profile '{request.profile}' not found"
                    )
                
                # Apply profile patterns
                for rule in profile.patterns:
                    if rule.enabled:
                        engine.pattern_registry.add_pattern(
                            f"profile_{rule.pattern}",
                            rule.pattern
                        )
            
            # Perform sanitization
            sanitized_text, traces = engine.redact_text(request.text)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Update server stats
            server_stats["requests_processed"] += 1
            server_stats["total_redactions"] += len(traces)
            
            # Prepare response
            response = SanitizeTextResponse(
                sanitized_text=sanitized_text,
                redaction_count=len(traces),
                processing_time_ms=processing_time_ms,
                trace=[trace.__dict__ for trace in traces] if request.trace else None
            )
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/sanitize/file",
              tags=["Sanitization"],
              summary="Sanitize uploaded file",
              description="Upload and sanitize a log file with optional profile")
    async def sanitize_file(
        file: UploadFile = File(..., description="Log file to sanitize"),
        profile: Optional[str] = Form(None, description="Redaction profile to use"),
        trace: bool = Form(False, description="Generate redaction trace")
    ):
        """Sanitize an uploaded file."""
        try:
            # Validate file type
            allowed_extensions = {'.log', '.txt', '.out', '.err', '.json', '.yaml', '.yml'}
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions and 'log' not in file.filename.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                )
            
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Configure engine
            engine = RedactionEngine()
            engine.configure({'trace_enabled': trace})
            
            # Load profile if specified
            if profile:
                profile_obj = profile_manager.get_profile(profile)
                if not profile_obj:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Profile '{profile}' not found"
                    )
                
                # Apply profile patterns
                for rule in profile_obj.patterns:
                    if rule.enabled:
                        engine.pattern_registry.add_pattern(
                            f"profile_{rule.pattern}",
                            rule.pattern
                        )
            
            start_time = datetime.now()
            
            # Perform sanitization
            sanitized_content, traces = engine.redact_text(text_content, file.filename)
            
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Update server stats
            server_stats["requests_processed"] += 1
            server_stats["total_redactions"] += len(traces)
            
            # Create temporary file for download
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_sanitized{file_extension}') as tmp_file:
                tmp_file.write(sanitized_content)
                tmp_file_path = tmp_file.name
            
            # Prepare response
            response_data = {
                "filename": f"{Path(file.filename).stem}_sanitized{file_extension}",
                "redaction_count": len(traces),
                "processing_time_ms": processing_time_ms,
                "file_size_bytes": len(sanitized_content.encode('utf-8'))
            }
            
            if trace:
                response_data["trace"] = [trace.__dict__ for trace in traces]
            
            return FileResponse(
                tmp_file_path,
                media_type='application/octet-stream',
                filename=response_data["filename"],
                headers={"X-LogVeil-Stats": json.dumps(response_data)}
            )
            
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be text-based and UTF-8 encoded")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/profiles",
             response_model=List[ProfileInfo],
             tags=["Configuration"],
             summary="List available profiles",
             description="Get list of all available redaction profiles")
    async def list_profiles():
        """List all available redaction profiles."""
        profiles = []
        for name in profile_manager.list_profiles():
            profile = profile_manager.get_profile(name)
            profiles.append(ProfileInfo(
                name=name,
                description=profile.description,
                log_format=profile.log_format.value,
                pattern_count=len(profile.patterns),
                key_path_count=len(profile.key_paths)
            ))
        return profiles
    
    @app.get("/profiles/{profile_name}",
             tags=["Configuration"],
             summary="Get profile details",
             description="Get detailed information about a specific profile")
    async def get_profile(profile_name: str):
        """Get details of a specific profile."""
        profile = profile_manager.get_profile(profile_name)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Profile '{profile_name}' not found")
        
        return profile.to_dict()
    
    @app.get("/status",
             response_model=ServerStats,
             tags=["Monitoring"],
             summary="Get server status",
             description="Get current server statistics and status")
    async def get_status():
        """Get server status and statistics."""
        uptime = (datetime.now() - server_stats["start_time"]).total_seconds()
        
        return ServerStats(
            requests_processed=server_stats["requests_processed"],
            total_redactions=server_stats["total_redactions"],
            uptime_seconds=uptime,
            available_profiles=profile_manager.list_profiles(),
            active_engine="python"  # This would come from dispatcher in full implementation
        )
    
    @app.post("/batch/sanitize",
              tags=["Batch Processing"],
              summary="Batch sanitize multiple texts",
              description="Sanitize multiple text inputs in a single request")
    async def batch_sanitize(
        texts: List[str] = Field(..., description="List of texts to sanitize"),
        profile: Optional[str] = Query(None, description="Redaction profile to use"),
        entropy_threshold: float = Query(4.2, description="Entropy threshold")
    ):
        """Batch sanitize multiple text inputs."""
        try:
            # Configure engine
            engine = RedactionEngine()
            engine.configure({
                'entropy_threshold': entropy_threshold,
                'enable_entropy_detection': True,
                'trace_enabled': False
            })
            
            # Load profile if specified
            if profile:
                profile_obj = profile_manager.get_profile(profile)
                if profile_obj:
                    for rule in profile_obj.patterns:
                        if rule.enabled:
                            engine.pattern_registry.add_pattern(
                                f"profile_{rule.pattern}",
                                rule.pattern
                            )
            
            results = []
            total_redactions = 0
            
            start_time = datetime.now()
            
            for i, text in enumerate(texts):
                sanitized_text, traces = engine.redact_text(text)
                total_redactions += len(traces)
                
                results.append({
                    "index": i,
                    "sanitized_text": sanitized_text,
                    "redaction_count": len(traces)
                })
            
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Update server stats
            server_stats["requests_processed"] += 1
            server_stats["total_redactions"] += total_redactions
            
            return {
                "results": results,
                "summary": {
                    "total_inputs": len(texts),
                    "total_redactions": total_redactions,
                    "processing_time_ms": processing_time_ms
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


if __name__ == "__main__":
    # For development/testing
    import uvicorn
    from core.redactor import RedactionEngine
    from core.profiles import ProfileManager
    
    engine = RedactionEngine()
    profile_mgr = ProfileManager()
    app = create_app(engine, profile_mgr)
    
    uvicorn.run(app, host="127.0.0.1", port=8080)
