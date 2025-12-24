import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取API基础URL，支持环境变量和默认值
  const getApiUrl = () => {
    // 首先检查是否有环境变量设置
    const envUrl = import.meta.env.VITE_API_URL;
    if (envUrl) {
      return envUrl;
    }
    // 否则使用相对路径（会自动适配当前域名）
    return '';
  };

  const apiBaseUrl = getApiUrl();

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setError('请选择一张图片');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`http://139.224.207.84:8000/api/ocr`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '上传失败');
      }

      const data = await response.json();
      setResult(data);
      setSelectedFile(null);
    } catch (err) {
      setError(err.message || '处理图片时出错');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>图片识别服务</h1>
        <p className="subtitle">上传图片进行文字识别</p>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="file-input"
              onChange={handleFileChange}
              accept="image/png,image/jpeg,image/gif,image/webp"
              disabled={loading}
            />
            <label htmlFor="file-input" className="file-label">
              {selectedFile
                ? `已选择: ${selectedFile.name}`
                : '点击选择图片或拖拽图片'}
            </label>
          </div>

          <button type="submit" disabled={loading || !selectedFile} className="submit-btn">
            {loading ? '处理中...' : '开始识别'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <div className="result-header">
              <h2>识别结果</h2>
              <p className="result-meta">
                文件: {result.image_file} | 字符数: {result.text_length}
              </p>
            </div>
            <div className="result-content">
              <p>{result.ocr_result}</p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(result.ocr_result);
                alert('已复制到剪贴板');
              }}
              className="copy-btn"
            >
              📋 复制结果
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
