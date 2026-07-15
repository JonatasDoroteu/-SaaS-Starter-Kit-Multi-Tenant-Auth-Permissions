import { useEffect, useRef, useState } from 'react';
import UsagePanel from './UsagePanel';
import ApiKeysPanel from './ApiKeysPanel';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [orgName, setOrgName] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [orgs, setOrgs] = useState([]);
  const [selectedOrgId, setSelectedOrgId] = useState(null);
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const usagePanelRef = useRef(null);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/api/v1/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setOrgs(data))
      .catch(() => setOrgs([]));
  }, [token]);

  useEffect(() => {
    if (selectedOrgId && usagePanelRef.current) {
      usagePanelRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [selectedOrgId]);

  const handleAuth = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage('');
    try {
      const endpoint = mode === 'login' ? '/api/v1/auth/login' : '/api/v1/auth/register';
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.access_token) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        setMessage(mode === 'login' ? 'Logged in successfully' : 'Registered successfully');
      } else {
        setMessage(data.detail || 'Authentication failed');
      }
    } catch (error) {
      setMessage('Unable to reach the backend. Check if the server is running.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateOrg = async (event) => {
    event.preventDefault();
    const response = await fetch(`${API_URL}/api/v1/organizations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: orgName }),
    });
    const data = await response.json();
    if (response.ok) {
      setOrgs((prev) => [...prev, data]);
      setSelectedOrgId(data.id);
      setOrgName('');
      setMessage('Organization created');
    } else {
      setMessage(data.detail || 'Failed to create organization');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setOrgs([]);
    setSelectedOrgId(null);
    setMessage('Logged out');
  };

  return (
    <div className="app-shell">
      <span className="app-eyebrow">Multi-tenant infrastructure</span>
      <h1>SaaS Starter</h1>

      <div className="app-header-row">
        <p>Multi-tenant auth, organizations and invites in one place.</p>
        {token ? (
          <button type="button" className="secondary" onClick={handleLogout}>
            Logout
          </button>
        ) : null}
      </div>

      {!token ? (
        <form onSubmit={handleAuth} className="card">
          <h2>{mode === 'login' ? 'Login' : 'Register'}</h2>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
          <button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Working...' : mode === 'login' ? 'Login' : 'Register'}</button>
          <button type="button" className="secondary" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            Switch to {mode === 'login' ? 'register' : 'login'}
          </button>
        </form>
      ) : (
        <>
          <form onSubmit={handleCreateOrg} className="card">
            <h2>Create organization</h2>
            <input value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Organization name" />
            <button type="submit">Create</button>
          </form>

          <div className="card">
            <h2>Your organizations</h2>
            {orgs.length === 0 ? (
              <p>No organizations yet.</p>
            ) : (
              <ul>
                {orgs.map((org) => (
                  <li
                    key={org.id}
                    onClick={() => setSelectedOrgId(org.id)}
                    className={`org-item ${selectedOrgId === org.id ? 'selected' : ''}`}
                  >
                    {org.name}
                    {selectedOrgId === org.id ? <span className="tag">Active</span> : null}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div ref={usagePanelRef}>
            <UsagePanel token={token} organizationId={selectedOrgId} />
            <ApiKeysPanel token={token} organizationId={selectedOrgId} />
          </div>
        </>
      )}

      {message ? <p className="message">{message}</p> : null}
    </div>
  );
}

export default App;