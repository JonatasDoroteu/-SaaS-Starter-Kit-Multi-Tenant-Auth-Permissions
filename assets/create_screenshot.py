from pathlib import Path

root = Path(__file__).resolve().parent
output = root / 'screenshot.png'

svg = '''<svg width="1280" height="720" xmlns="http://www.w3.org/2000/svg">
  <rect width="1280" height="720" fill="#0f172a"/>
  <rect x="0" y="0" width="1280" height="120" fill="#111827"/>
  <rect x="150" y="140" width="980" height="480" rx="28" fill="#111827" stroke="#334155" stroke-width="3"/>
  <text x="220" y="220" fill="#f8fafc" font-family="Segoe UI, Arial, sans-serif" font-size="42" font-weight="700">SaaS Starter</text>
  <text x="220" y="280" fill="#cbd5e1" font-family="Segoe UI, Arial, sans-serif" font-size="24">FastAPI + React + Multi-Tenant Auth</text>
  <text x="220" y="330" fill="#cbd5e1" font-family="Segoe UI, Arial, sans-serif" font-size="24">JWT, Organizations, Memberships &amp; Invites</text>
  <rect x="220" y="370" width="360" height="46" rx="10" fill="#1f2937" stroke="#475569"/>
  <text x="245" y="400" fill="#94a3b8" font-family="Segoe UI, Arial, sans-serif" font-size="18">Email</text>
  <rect x="220" y="450" width="360" height="46" rx="10" fill="#1f2937" stroke="#475569"/>
  <text x="245" y="480" fill="#94a3b8" font-family="Segoe UI, Arial, sans-serif" font-size="18">Password</text>
  <rect x="220" y="530" width="200" height="48" rx="12" fill="#2563eb"/>
  <text x="280" y="562" fill="white" font-family="Segoe UI, Arial, sans-serif" font-size="22" text-anchor="middle">Login</text>
  <rect x="700" y="280" width="320" height="260" rx="22" fill="#0b1220" stroke="#334155" stroke-width="2"/>
  <text x="740" y="330" fill="#f8fafc" font-family="Segoe UI, Arial, sans-serif" font-size="24">Organizations</text>
  <text x="740" y="380" fill="#93c5fd" font-family="Segoe UI, Arial, sans-serif" font-size="20">Acme</text>
  <text x="740" y="430" fill="#93c5fd" font-family="Segoe UI, Arial, sans-serif" font-size="20">Globex</text>
  <text x="740" y="480" fill="#93c5fd" font-family="Segoe UI, Arial, sans-serif" font-size="20">Northwind</text>
</svg>'''

output.write_text(svg, encoding='utf-8')
print(output)
