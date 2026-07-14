import { useEffect, useState } from 'react';

const API_URL = 'http://127.0.0.1:8000';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function ApiKeysPanel({ token, organizationId }) {
  const [keys, setKeys] = useState([]);
  const [name, setName] = useState('');
  const [reveal, setReveal] = useState(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const loadKeys = () => {
    if (!token || !organizationId) return;
    fetch(`${API_URL}/api/v1/api-keys`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'X-Organization-Id': organizationId,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load keys');
        return res.json();
      })
      .then((data) => {
        setKeys(data);
        setError('');
      })
      .catch(() => setError('Could not load API keys.'));
  };

  useEffect(() => {
    loadKeys();
    setReveal(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, organizationId]);

  const handleCreate = async (event) => {
    event.preventDefault();
    if (!name.trim()) return;
    setIsCreating(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/api/v1/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Organization-Id': organizationId,
        },
        body: JSON.stringify({ name }),
      });
      const data = await response.json();
      if (response.ok) {
        setReveal(data);
        setName('');
        loadKeys();
      } else {
        setError(data.detail || 'Failed to create API key');
      }
    } catch (err) {
      setError('Could not reach the backend.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleCopy = () => {
    if (!reveal) return;
    navigator.clipboard.writeText(reveal.api_key).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleSeal = () => {
    setReveal(null);
    setCopied(false);
  };

  const handleRevoke = async (keyId) => {
    const ok = window.confirm('Revoke this key? Any integration using it will stop working immediately.');
    if (!ok) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Organization-Id': organizationId,
        },
      });
      if (response.ok || response.status === 204) {
        loadKeys();
      } else {
        setError('Failed to revoke key');
      }
    } catch (err) {
      setError('Could not reach the backend.');
    }
  };

  if (!organizationId) {
    return (
      <div className="card">
        <span className="ticket-label">API Keys</span>
        <p className="ticket-caption">Select an organization above to manage its API keys.</p>
      </div>
    );
  }

  return (
    <div className="card vault-card">
      <div className="vault-header">
        <h2>API Keys</h2>
        <span className="vault-count">{keys.length} issued</span>
      </div>

      <form className="vault-create" onSubmit={handleCreate}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Key name (e.g. production-server)"
        />
        <button type="submit" disabled={isCreating}>
          {isCreating ? 'Issuing...' : 'Issue key'}
        </button>
      </form>

      {reveal ? (
        <div className="key-reveal">
          <span className="key-reveal-label">Issued — visible once</span>
          <code className="key-reveal-value">{reveal.api_key}</code>
          <div className="key-reveal-actions">
            <button type="button" onClick={handleCopy}>
              {copied ? 'Copied' : 'Copy key'}
            </button>
            <button type="button" className="secondary" onClick={handleSeal}>
              I&apos;ve saved it — seal
            </button>
          </div>
          <span className="key-reveal-caption">
            This key won&apos;t be shown again. Store it in your secrets manager or .env now.
          </span>
        </div>
      ) : null}

      {error ? (
        <div className="ticket-alert" style={{ margin: '0 1.5rem 1rem' }}>
          {error}
        </div>
      ) : null}

      {keys.length === 0 ? (
        <div className="key-empty">No keys issued yet. Create one above to authenticate API requests.</div>
      ) : (
        <div className="key-ledger">
          {keys.map((key) => (
            <div key={key.id} className={`key-row ${key.revoked_at ? 'revoked' : ''}`}>
              <div className="key-row-main">
                <span className="key-row-name">{key.name}</span>
                <span className="key-row-prefix">{key.prefix}••••••••••••••••</span>
                <span className="key-row-date">
                  Issued {formatDate(key.created_at)}
                  {key.last_used_at ? ` · Last used ${formatDate(key.last_used_at)}` : ' · Never used'}
                </span>
              </div>
              <span className={`stamp ${key.revoked_at ? 'revoked' : 'active'}`}>
                {key.revoked_at ? 'Revoked' : 'Active'}
              </span>
              {key.revoked_at ? (
                <span />
              ) : (
                <button type="button" className="revoke-btn" onClick={() => handleRevoke(key.id)}>
                  Revoke
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ApiKeysPanel;