# Julius.ai API Integration Setup Guide

## 🚀 Overview
This guide will help you integrate your Synthetic Data Generator with the Julius.ai API for enhanced demographic analytics and data generation.

## 📋 Prerequisites

1. **Julius.ai Account**: Sign up at [julius.ai](https://julius.ai)
2. **API Key**: Get your API key from the Julius.ai dashboard
3. **Python Dependencies**: Install required packages

## 🔧 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install requests python-dotenv
```

Or update your existing installation:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. **Copy the sample configuration:**
   ```bash
   cp julius_ai_config.env .env
   ```

2. **Edit your `.env` file:**
   ```env
   # Julius.ai API Configuration
   JULIUS_AI_API_KEY=your_actual_api_key_here
   JULIUS_AI_BASE_URL=https://api.julius.ai/v1
   APP_URL=http://localhost:5000
   JULIUS_AI_ENABLED=true
   JULIUS_AI_TIMEOUT=30
   JULIUS_AI_AUTO_FALLBACK=true
   
   # Your existing environment variables...
   OPENROUTER_API_KEY=your_openrouter_key
   MODEL_ID=deepseek/deepseek-r1:free
   ```

### Step 3: Verify Integration

1. **Start your application:**
   ```bash
   python app.py
   ```

2. **Check Julius.ai status:**
   Visit: `http://localhost:5000/julius-status`

   Expected response:
   ```json
   {
     "success": true,
     "julius_status": {
       "api_enabled": true,
       "connection_status": "connected",
       "api_version": "1.0",
       "rate_limit_remaining": "1000",
       "message": "Connected to Julius.ai API"
     },
     "timestamp": "2025-01-XX..."
   }
   ```

## 🎯 Features Enabled

### 1. **Real-time Demographic Analysis**
- Age distribution optimization
- Regional demographic patterns
- Realistic email provider distributions
- Name patterns based on demographics

### 2. **API-Powered Data Enhancement**
- Automatic field enhancement using Julius.ai
- Intelligent outlier generation
- Advanced data validation
- Quality scoring and suggestions

### 3. **Graceful Fallback**
- Automatic fallback to local processing if API is unavailable
- Rate limit handling
- Error recovery
- Hybrid processing modes

## 🔍 Usage Examples

### Basic Usage (via UI)
1. Select "Online Mode"
2. Check "Enable Julius AI Analytics"
3. Choose demographic settings:
   - Age Distribution: Gen-Z focused
   - Regional Demographics: North America
4. Generate data - Julius.ai will enhance it automatically

### API Usage
```python
# The system automatically uses Julius.ai when enabled
julius_result = julius_analytics.analyze_and_enhance_data(
    data=your_data,
    advanced_options={
        'age_distribution': 'gen-z',
        'demographics_region': 'north-america',
        'include_outliers': True
    }
)

print(f"Source: {julius_result['source']}")  # 'julius_ai_api' or 'local_processing'
print(f"Tokens used: {julius_result['tokens_used']}")
```

## 📊 Analytics Enhancement

When Julius.ai is enabled, your analytics reports will include:

```json
{
  "analytics_summary": {
    "total_records": 100,
    "demographic_analysis": {...},
    "julius_ai_info": {
      "processing_time": 1.2,
      "tokens_used": 150,
      "data_source": "julius_ai_api",
      "api_success": true,
      "enhanced_records": 100
    }
  }
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JULIUS_AI_API_KEY` | Your Julius.ai API key | Required |
| `JULIUS_AI_BASE_URL` | API endpoint URL | `https://api.julius.ai/v1` |
| `JULIUS_AI_ENABLED` | Enable/disable API | `true` |
| `JULIUS_AI_TIMEOUT` | Request timeout (seconds) | `30` |
| `JULIUS_AI_AUTO_FALLBACK` | Auto fallback on errors | `true` |

### Python Configuration

```python
# Initialize with custom settings
julius_analytics = JuliusAnalytics(use_api=True)

# Check connection status
status = julius_analytics.get_connection_status()

# Force local mode for testing
julius_analytics = JuliusAnalytics(use_api=False)
```

## 🚨 Troubleshooting

### Common Issues

1. **"Julius.ai API connection failed"**
   - Check your API key in `.env`
   - Verify internet connection
   - Check Julius.ai service status

2. **"No Julius.ai API key configured"**
   - Add `JULIUS_AI_API_KEY` to your `.env` file
   - Restart the application

3. **Rate Limit Exceeded**
   - System automatically falls back to local processing
   - Check your Julius.ai plan limits
   - Consider upgrading your plan

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View logs for:
- API connection attempts
- Fallback triggers
- Processing time metrics
- Token usage

## 📈 Performance Metrics

### API vs Local Processing

| Feature | Julius.ai API | Local Processing |
|---------|---------------|------------------|
| Speed | 1-3 seconds | <0.1 seconds |
| Quality | Advanced AI | Rule-based |
| Cost | Token-based | Free |
| Availability | Depends on API | Always available |

### Hybrid Approach Benefits

- **Best of both worlds**: High-quality API enhancement with reliable fallback
- **Cost optimization**: Only use API tokens when needed
- **High availability**: Never fails completely
- **Gradual scaling**: Start with local, upgrade to API as needed

## 📞 Support

### Julius.ai API Issues
- Julius.ai Documentation: [docs.julius.ai](https://docs.julius.ai)
- Support: support@julius.ai

### Integration Issues
- Check the `/julius-status` endpoint
- Review application logs
- Verify environment configuration

## 🔄 Migration from Local-Only

If you were using the previous local-only version:

1. **Backup your current setup**
2. **Install new dependencies**: `pip install requests python-dotenv`
3. **Add environment variables** to `.env`
4. **Test the integration** using `/julius-status`
5. **Gradual rollout**: Start with `JULIUS_AI_ENABLED=false` and enable when ready

The system is fully backward compatible - existing functionality remains unchanged.
