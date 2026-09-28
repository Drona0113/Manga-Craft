import React from 'react'

function App() {
  return (
    <div className="app">
      <header>
        <h1>MangaCraft V3</h1>
        <p>AI-powered manga creation workspace</p>
      </header>
      <main>
        <div className="status">
          <h2>Development Status</h2>
          <p>Phase: V3.1 - Project Structure & Environment Setup</p>
          <div className="api-status">
            <h3>API Status</h3>
            <button onClick={checkApi}>Check API</button>
            <p id="api-response">Click to check API status</p>
          </div>
        </div>
      </main>
    </div>
  )
}

async function checkApi() {
  try {
    const response = await fetch('http://localhost:8000/health')
    const data = await response.json()
    document.getElementById('api-response').textContent = 
      `Status: ${data.status}`
  } catch (error) {
    document.getElementById('api-response').textContent = 
      `Error: ${error.message}`
  }
}

export default App
