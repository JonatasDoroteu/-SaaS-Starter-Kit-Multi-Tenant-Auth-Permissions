import { useEffect, useState } from 'react';

const API_URL = 'http://127.0.0.1:8000';

function UsagePanel({ token, organizationId }) {
  const [usage, setUsage] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token || !organizationId) return;

    fetch(`${API_URL}/api/v1/usage`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'X-Organization-Id': organizationId,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load usage');
        return res.json();
      })
      .then((data) => {
        setUsage(data);
        setError('');
      })
      .catch(() => setError('Could not load usage. Check your connection and try again.'));
  }, [token, organizationId]);

  if (!organizationId) {
    return (
      <div className="card">
        <span className="ticket-label">Usage</span>
        <p className="ticket-caption">Select an organization above to see its API usage.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <span className="ticket-label">Usage</span>
        <div className="ticket-alert">{error}</div>
      </div>
    );
  }

  if (!usage) {
    return (
      <div className="card">
        <span className="ticket-label">Usage</span>
        <p className="ticket-caption">Loading...</p>
      </div>
    );
  }

  const aiUsage = usage.usage.find((item) => item.feature === 'ai_analysis');
  const count = aiUsage ? aiUsage.count : 0;
  const limit = usage.limit;
  const isUnlimited = limit === null;
  const isAtLimit = !isUnlimited && count >= limit;
  const isNearLimit = !isUnlimited && count >= limit * 0.7;

  return (
    <div className="card usage-ticket">
      <div className="ticket-top">
        <span className={`ticket-plan ${usage.plan}`}>{usage.plan} plan</span>
        <span className="ticket-period">{usage.period}</span>
      </div>

      <div className="ticket-tear" />

      <div className="ticket-body">
        <span className="ticket-label">AI analyses this month</span>

        {isUnlimited ? (
          <span className="ticket-unlimited">
            {count} <span className="infinity">/ &infin;</span>
          </span>
        ) : (
          <div className="punch-row">
            {Array.from({ length: limit }).map((_, index) => (
              <div
                key={index}
                className={`punch ${index < count ? 'filled' : ''} ${isAtLimit ? 'critical' : ''}`}
              />
            ))}
          </div>
        )}

        {isAtLimit ? (
          <div className="ticket-alert">
            Monthly limit reached. Upgrade to Pro for unlimited analyses.
          </div>
        ) : (
          <span className="ticket-caption">
            {isUnlimited
              ? 'No monthly limit on the Pro plan.'
              : `${count} of ${limit} used · ${limit - count} remaining`}
          </span>
        )}
      </div>
    </div>
  );
}

export default UsagePanel;