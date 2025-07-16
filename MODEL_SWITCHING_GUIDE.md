# Dynamic Model Switching Guide

## 🚀 **FEATURE OVERVIEW**

The Contract Analyzer now supports **dynamic model switching** - allowing you to change the LLM model while the application is running without restarting the server.

## ✨ **KEY FEATURES**

### 🔄 **Real-time Model Switching**
- Switch between any installed Ollama models instantly
- No server restart required
- Automatic model validation and testing
- Graceful fallback if model change fails

### 🔍 **Model Discovery**
- Automatically detects all available models
- Shows model details (size, quantization, family)
- Real-time model availability checking
- Health status monitoring

### 🛡️ **Robust Error Handling**
- Validates model existence before switching
- Tests new model with sample prompt
- Automatic rollback on failure
- Clear error messages with available alternatives

### 🎯 **User-friendly Interface**
- Dropdown selector with model sizes
- Current model status display
- Real-time notifications
- Model switching progress indicators

## 📋 **AVAILABLE MODELS**

Based on your current installation, the following models are available:

```
📊 Model Inventory:
├── llama3:latest (4.3 GB) - General purpose, balanced performance
├── llama3.2:latest (1.9 GB) - Smaller, faster alternative
├── deepseek-r1:14b (8.4 GB) - Advanced reasoning model
├── deepseek-r1:32b (18.5 GB) - Largest, most capable model
├── nomic-embed-text:latest (261 MB) - Text embeddings
├── Godmoded/llama3-lexi-uncensored:latest (4.6 GB) - Uncensored variant
└── tinyllama:latest (608 MB) - Fastest, smallest model
```

## 🔧 **HOW TO USE**

### Via Web Interface

1. **Navigate to Settings Tab**
   - Click on the ⚙️ Settings tab in the sidebar
   - Find the "System Settings" section

2. **Select New Model**
   - Use the "LLM Model" dropdown
   - Models show name and size: `llama3:latest (4.3 GB)`
   - Current model is pre-selected

3. **Confirm Change**
   - Select desired model
   - Confirm the change in the popup dialog
   - Wait for validation and testing

4. **Monitor Status**
   - Watch for success/error notifications
   - Check header for current model display
   - Model info updates automatically

### Via API

#### Get Available Models
```bash
curl -s http://localhost:5000/api/available-models | jq '.'
```

#### Change Model
```bash
curl -s -X POST http://localhost:5000/api/change-model \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:latest"}' | jq '.'
```

#### Get Current Model Info
```bash
curl -s http://localhost:5000/api/model-info | jq '.'
```

## 📊 **API ENDPOINTS**

### `GET /api/available-models`
Returns list of available models with detailed information.

**Response:**
```json
{
  "success": true,
  "current_model": "llama3:latest",
  "models": [
    {
      "name": "llama3:latest",
      "size": 4661224676,
      "details": {
        "parameter_size": "8.0B",
        "quantization_level": "Q4_0",
        "family": "llama"
      },
      "current": true
    }
  ]
}
```

### `POST /api/change-model`
Changes the current model with validation and testing.

**Request:**
```json
{
  "model": "llama3.2:latest"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model changed to 'llama3.2:latest' successfully",
  "previous_model": "llama3:latest",
  "current_model": "llama3.2:latest"
}
```

### `GET /api/model-info`
Returns detailed information about the current model.

**Response:**
```json
{
  "name": "llama3:latest",
  "host": "http://localhost:11434",
  "connection_healthy": true,
  "available_models": ["llama3:latest", "llama3.2:latest", ...],
  "info": {
    "size": 4661224676,
    "details": {...}
  }
}
```

## 🎨 **UI COMPONENTS**

### Header Status Display
- Shows current model name and size
- Health indicator with color coding:
  - 🟢 Green: Healthy and connected
  - 🟡 Yellow: Degraded performance
  - 🔴 Red: Connection issues

### Settings Panel
- Model selector dropdown
- Current model information display
- Real-time model switching

### Notifications
- Success: ✅ Model changed successfully
- Error: ❌ Model change failed
- Warning: ⚠️ Model not available
- Info: ℹ️ Model switching in progress

## 🔐 **SECURITY FEATURES**

### Input Validation
- Sanitizes model names
- Validates model existence
- Prevents injection attacks

### Audit Logging
- All model changes are logged
- Includes user IP and timestamp
- Success/failure tracking

### Error Handling
- Graceful degradation
- Automatic fallback
- Clear error messages

## 🚀 **PERFORMANCE CONSIDERATIONS**

### Model Switching Speed
- **Small models** (< 1GB): ~1-2 seconds
- **Medium models** (1-5GB): ~3-5 seconds
- **Large models** (> 5GB): ~5-10 seconds

### Memory Usage
- Only one model active at a time
- Automatic cleanup of previous model
- Memory-efficient switching

### Testing Process
Each model change includes:
1. Availability validation
2. Connection testing
3. Sample prompt execution
4. Response validation
5. Health status update

## 🔧 **TROUBLESHOOTING**

### Common Issues

#### "Model not available"
- **Cause**: Model not installed in Ollama
- **Solution**: Run `ollama pull <model-name>`

#### "Model change failed"
- **Cause**: Model failed testing
- **Solution**: Check Ollama service status

#### "Connection issues"
- **Cause**: Ollama service not running
- **Solution**: Start Ollama with `ollama serve`

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Model 'X' not available` | Model not installed | `ollama pull X` |
| `Model change failed: timeout` | Model loading timeout | Check system resources |
| `Connection unhealthy` | Ollama not responding | Restart Ollama service |

## 📈 **BEST PRACTICES**

### Model Selection
- **For speed**: Use `tinyllama:latest` or `llama3.2:latest`
- **For accuracy**: Use `deepseek-r1:14b` or `llama3:latest`
- **For complex tasks**: Use `deepseek-r1:32b`

### Performance Optimization
- Switch to smaller models for development
- Use larger models for production analysis
- Monitor system resources during switching

### Monitoring
- Check health indicators regularly
- Monitor model switching notifications
- Review audit logs for issues

## 🎯 **FUTURE ENHANCEMENTS**

### Planned Features
- **Model Auto-selection**: Automatic model choice based on task
- **Performance Metrics**: Model speed and accuracy tracking
- **Model Preloading**: Pre-load models for faster switching
- **Custom Models**: Support for user-trained models

### API Improvements
- **Batch Model Operations**: Switch multiple models
- **Model Configuration**: Fine-tune model parameters
- **Usage Analytics**: Track model usage patterns

## 📞 **SUPPORT**

### Getting Help
- Check the dashboard health indicator
- Review the browser console for errors
- Monitor the server logs for detailed information

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment.

---

## 🎉 **CONCLUSION**

Dynamic model switching provides unprecedented flexibility for the Contract Analyzer, allowing you to:

- **Optimize performance** by choosing the right model for each task
- **Experiment easily** with different models without downtime
- **Scale efficiently** based on current needs
- **Maintain reliability** with robust error handling

The system is designed to be **user-friendly**, **secure**, and **performant**, ensuring a smooth experience while providing powerful model management capabilities.

**Happy analyzing!** 🚀 