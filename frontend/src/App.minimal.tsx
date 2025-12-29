// Minimal test App to verify React is working
import React from 'react'

export default function MinimalApp() {
  return (
    <div style={{ 
      padding: '2rem', 
      color: 'white', 
      background: '#050914', 
      minHeight: '100vh',
      fontFamily: 'system-ui'
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>✅ React is Working!</h1>
      <p>If you see this, React is rendering correctly.</p>
      <p>The issue is in the main App component or its dependencies.</p>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#1e293b', borderRadius: '0.5rem' }}>
        <h2>Next Steps:</h2>
        <ol style={{ marginLeft: '1.5rem' }}>
          <li>Check browser console (F12) for errors</li>
          <li>Check Network tab for failed file loads</li>
          <li>Gradually add back App components to find the issue</li>
        </ol>
      </div>
    </div>
  )
}




