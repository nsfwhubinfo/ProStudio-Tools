# Frame Pack Optimized Settings for RTX 4060

## ✅ CUDA Issue Fixed
- **Before**: PyTorch 2.7.1 with CUDA 11.8 (mismatch with system CUDA 12.8)
- **After**: PyTorch 2.5.1 with CUDA 12.1 (better compatibility)

## 🚀 Optimized Settings for RTX 4060

### Essential Settings:
1. **Video Length**: **5-10 seconds** (NOT 30!)
   - Start with 5 seconds
   - Each second = ~30 frames @ 30fps
   - 5 seconds = 150 frames total

2. **GPU Memory Preservation**: **8 GB**
   - Your GPU has 8GB total
   - Set to 8GB to avoid OOM errors

3. **Enable TeaCache**: ✅ **YES**
   - 40% faster generation
   - Better quality on hands/fingers

4. **Steps**: **25** (default)
   - Don't change this

5. **Image Size**: 
   - Start with **512x512**
   - Can try **768x512** later

## 📊 Expected Performance

With these settings on RTX 4060:
- **5-second video**: ~12-25 minutes
- **10-second video**: ~25-50 minutes
- **Per frame**: ~5-10 seconds

## 🎯 Step-by-Step Guide

1. **Access Frame Pack**: http://localhost:7860

2. **Upload Image**:
   - Use a clear, simple image
   - 512x512 or 768x512 works best

3. **Write Prompt**:
   - Be specific about motion
   - Example: "The person slowly turns their head to the right while smiling"

4. **Settings**:
   - Video Length: **5** seconds
   - GPU Memory: **8** GB
   - TeaCache: **☑️ Enabled**
   - Steps: **25**
   - Seed: **31337** (or any number)

5. **Click "Start Generation"**

## ⚠️ What NOT to Do

- ❌ Don't start with 30-second videos
- ❌ Don't use GPU Memory < 8GB
- ❌ Don't disable TeaCache
- ❌ Don't use huge images (>1024px)

## 🔧 Troubleshooting

If generation is slow or fails:
1. Reduce video length to 3 seconds
2. Use smaller image (512x512)
3. Restart Frame Pack
4. Check GPU memory: `nvidia-smi`

## 📈 Progress Monitoring

Frame Pack shows:
- Current frame being generated
- Total frames completed
- Estimated time remaining
- Live preview of generated frames

Remember: Frame Pack generates video progressively, so you'll see results building up frame by frame!