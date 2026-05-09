import { Activity, BarChart3, KeyRound, LogIn, ShieldCheck, UserPlus } from "lucide-react";
import { useMemo, useState } from "react";

import { fetchEvidencePackage, loginUser, registerUser } from "./api/client";

const tiers = [
  { id: "newbie", label: "Newbie", detail: "Plain-language verdicts" },
  { id: "intermediate", label: "Intermediate", detail: "Indicators and model summaries" },
  { id: "pro", label: "Pro", detail: "Full debate data and exports" },
];

export default function App() {
  const [mode, setMode] = useState("register");
  const [email, setEmail] = useState("demo@stockdebate.ai");
  const [password, setPassword] = useState("password123");
  const [tier, setTier] = useState("newbie");
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const activeTier = useMemo(() => tiers.find((item) => item.id === tier), [tier]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const payload = { email, password };
      const data =
        mode === "register"
          ? await registerUser({ ...payload, tier })
          : await loginUser(payload);
      setSession(data);
      setTier(data.user.tier);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-ink text-slate-100">
      <section className="mx-auto grid min-h-screen max-w-6xl gap-8 px-5 py-8 xl:grid-cols-[1fr_420px] xl:items-center xl:px-8">
        <div className="space-y-8">
          <nav className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded bg-cyan text-ink">
                <Activity size={22} strokeWidth={2.5} />
              </div>
              <div>
                <p className="text-lg font-semibold">StockDebate.AI</p>
                <p className="text-sm text-slate-400">Module 1 auth skeleton</p>
              </div>
            </div>
            <span className="rounded border border-line px-3 py-1 text-sm text-slate-300">
              M1 enabled
            </span>
          </nav>

          <div className="max-w-2xl space-y-6">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan">
              AI stock debate engine
            </p>
            <h1 className="text-4xl font-semibold leading-tight text-white md:text-5xl">
              Sign in, pick a tier, and prepare the debate workspace.
            </h1>
            <p className="max-w-xl text-base leading-7 text-slate-300">
              This first module sets up the app shell, user profile shape, JWT session flow,
              and feature flags the market data and model modules will build on.
            </p>
          </div>

          <div className="grid max-w-3xl gap-4 sm:grid-cols-3">
            <SignalCard icon={ShieldCheck} label="JWT Auth" value="Ready" />
            <SignalCard icon={BarChart3} label="Debate Engine" value="Flagged off" />
            <SignalCard icon={KeyRound} label="Tier Profile" value={activeTier.label} />
          </div>
        </div>

        <section className="rounded-lg border border-line bg-panel p-5 shadow-2xl shadow-cyan/10">
          {session ? (
            <ProfilePanel session={session} onSignOut={() => setSession(null)} />
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="flex rounded-md border border-line bg-ink p-1">
                <button
                  className={tabClass(mode === "register")}
                  type="button"
                  onClick={() => setMode("register")}
                >
                  <UserPlus size={16} />
                  Register
                </button>
                <button
                  className={tabClass(mode === "login")}
                  type="button"
                  onClick={() => setMode("login")}
                >
                  <LogIn size={16} />
                  Login
                </button>
              </div>

              <label className="block space-y-2">
                <span className="text-sm font-medium text-slate-300">Email</span>
                <input
                  className="field"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm font-medium text-slate-300">Password</span>
                <input
                  className="field"
                  type="password"
                  value={password}
                  minLength={8}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
              </label>

              {mode === "register" && (
                <div className="space-y-3">
                  <span className="text-sm font-medium text-slate-300">Experience tier</span>
                  <div className="grid gap-3">
                    {tiers.map((item) => (
                      <button
                        className={`tier-button ${tier === item.id ? "tier-button-active" : ""}`}
                        key={item.id}
                        type="button"
                        onClick={() => setTier(item.id)}
                      >
                        <span className="font-semibold">{item.label}</span>
                        <span className="text-sm text-slate-400">{item.detail}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                  {error}
                </div>
              )}

              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? "Working..." : mode === "register" ? "Create Account" : "Login"}
              </button>
            </form>
          )}
        </section>
      </section>
    </main>
  );
}

function SignalCard({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-line bg-panel p-4">
      <Icon className="mb-4 text-cyan" size={22} />
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 font-semibold text-white">{value}</p>
    </div>
  );
}

function ProfilePanel({ session, onSignOut }) {
  const [ticker, setTicker] = useState("AAPL");
  const [evidence, setEvidence] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleFetchEvidence(event) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const data = await fetchEvidencePackage(ticker, session.access_token);
      setEvidence(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">Signed in as</p>
          <p className="font-semibold text-white">{session.user.email}</p>
        </div>
        <span className="rounded bg-mint px-3 py-1 text-sm font-semibold text-ink">
          {session.user.tier}
        </span>
      </div>
      <div className="rounded-lg border border-line bg-ink p-4 text-sm text-slate-300">
        <p>User ID</p>
        <p className="mt-1 break-all font-mono text-slate-100">{session.user.user_id}</p>
      </div>

      <form className="space-y-3 rounded-lg border border-line bg-ink p-4" onSubmit={handleFetchEvidence}>
        <div className="flex items-center justify-between gap-3">
          <label className="flex-1 space-y-2">
            <span className="text-sm font-medium text-slate-300">Ticker evidence</span>
            <input
              className="field"
              maxLength={5}
              value={ticker}
              onChange={(event) => setTicker(event.target.value.toUpperCase())}
            />
          </label>
          <button className="mini-button mt-7" disabled={isLoading} type="submit">
            {isLoading ? "..." : "Fetch"}
          </button>
        </div>

        {error && <p className="text-sm text-red-200">{error}</p>}

        {evidence && (
          <div className="grid gap-3 pt-2 text-sm">
            <EvidenceRow label="Price" value={`$${evidence.price_volume.current_price}`} />
            <EvidenceRow label="Daily Change" value={`${evidence.price_volume.daily_change_percent}%`} />
            <EvidenceRow label="RSI" value={evidence.technicals?.rsi ?? "Missing"} />
            <EvidenceRow label="P/E" value={evidence.fundamentals?.pe_ratio ?? "Missing"} />
            <EvidenceRow
              label="Sentiment"
              value={`${evidence.news_sentiment?.aggregate_sentiment ?? "Missing"} (${evidence.news_sentiment?.aggregate_score ?? "n/a"})`}
            />
            <EvidenceRow label="Cache" value={`${evidence.cache.backend} ${evidence.cache.status}`} />
          </div>
        )}
      </form>

      <button className="secondary-button" type="button" onClick={onSignOut}>
        Sign Out
      </button>
    </div>
  );
}

function EvidenceRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded border border-line px-3 py-2">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold text-white">{value}</span>
    </div>
  );
}

function tabClass(isActive) {
  return `flex flex-1 items-center justify-center gap-2 rounded px-3 py-2 text-sm font-semibold transition ${
    isActive ? "bg-cyan text-ink" : "text-slate-300 hover:bg-white/5"
  }`;
}
