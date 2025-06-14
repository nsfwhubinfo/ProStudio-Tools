# ProStudio Tools Implementation Plan

## Current Status (Phase 1 Complete)

### ✅ Completed
1. **Project Structure**
   - Created `prostudio_tools/` directory hierarchy
   - Implemented base classes for video generation
   - Created Frame Pack generator wrapper

2. **Frame Pack Integration**
   - Selected Frame Pack as primary video generator (6GB VRAM requirement)
   - Implemented `FramePackGenerator` class with full API
   - Updated LTX-Video wrapper to use Frame Pack backend
   - Created test scripts (both real and mock versions)

3. **Architecture**
   - Modular design allowing easy addition of other models
   - Memory-conscious implementation with model loading/unloading
   - Proper logging and error handling structure

### 🚧 In Progress
1. **Dependencies Installation**
   ```bash
   pip install -r requirements_video.txt
   ```

2. **Model Downloads**
   - Frame Pack models from Hugging Face
   - VACE 1.3B as alternative option

## Next Steps (Priority Order)

### Phase 2: Audio Generation
1. **Text-to-Speech (Bark/XTTS)**
   ```python
   prostudio_tools/audio_gen/bark_tts.py
   prostudio_tools/audio_gen/xtts_tts.py
   ```

2. **Music/SFX Generation (AudioCraft)**
   ```python
   prostudio_tools/audio_gen/musicgen_audio.py
   ```

### Phase 3: Video Composition
1. **Audio-Video Synchronization**
   ```python
   prostudio_tools/editing/video_compositor.py
   ```

2. **Pipeline Orchestration**
   - Script → TTS → Video → Music → Final composition

### Phase 4: ContentEngine Integration
1. **Update Existing Mocks**
   - Replace `_generate_video_content()` in `devprompt_api.py`
   - Update `ContentEngine` to use real generators

2. **API Endpoints**
   - `/api/content/generate` - Full pipeline
   - `/api/content/status/{id}` - Progress tracking
   - `/api/content/download/{id}` - File retrieval

### Phase 5: AIOS Integration
1. **CORTEX-A Expert Agents**
   - VideoGenerationAgent
   - AudioGenerationAgent
   - CompositionAgent

2. **Workflow Automation**
   - Genetic algorithm optimization
   - Resource management
   - Queue management

## Resource Management Strategy

### Memory Constraints (Target: <10GB)
1. **Sequential Processing**
   - Load one model at a time
   - Unload after use with `torch.cuda.empty_cache()`

2. **Model Selection**
   - Frame Pack: 6GB (primary)
   - VACE 1.3B: 8GB (alternative)
   - Bark: ~2GB
   - MusicGen: ~3GB

3. **Optimization Techniques**
   - Use float16 precision
   - Implement batch processing where possible
   - Cache intermediate results

## Testing Strategy

### Unit Tests
- Individual generator tests
- Memory usage validation
- Error handling verification

### Integration Tests
- Full pipeline execution
- API endpoint testing
- Performance benchmarking

### Production Readiness
- Monitoring and logging
- Error recovery
- Queue management
- Result caching

## Command Reference

### Install Dependencies
```bash
# Core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements_video.txt
```

### Run Tests
```bash
# Mock test (no dependencies)
python3 test_framepack_mock.py

# Real test (requires dependencies)
python3 test_framepack.py

# LTX wrapper test
python3 ltx_video/bin/generate_video.py --prompt "test" --output test.mp4
```

### Start Services
```bash
# API server
python3 api_server.py

# Production server
python3 api_server_prod.py
```

## Success Metrics

1. **Functionality**
   - ✅ Real video files generated
   - ✅ Audio synchronized with video
   - ✅ Multiple format support

2. **Performance**
   - Target: <30s for 10-second video
   - Memory: <10GB peak usage
   - Quality: Comparable to commercial solutions

3. **Integration**
   - Seamless ContentEngine integration
   - Full API compatibility
   - AIOS orchestration ready

## Notes

- Frame Pack selected for low VRAM requirement (6GB)
- All models run locally without external APIs
- Modular design allows easy model swapping
- Focus on production readiness from start