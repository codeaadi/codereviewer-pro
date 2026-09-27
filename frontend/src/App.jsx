import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsCards from './components/MetricsCards';
import ReviewModel from './components/ReviewModel';
import { fetchReviews, triggerTestAudit } from './api/clients';
import { ShieldAlert, CheckCircle2, ChevronRight, Terminal } from 'lucide-react';

export default function App() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAuditing, setIsAuditing] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);

  const loadData = async () => {
    try {
      const data = await fetchReviews();
      setReviews(data);
    } catch (err) {
      console.error('Failed to load reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerAudit = async () => {
    setIsAuditing(true);
    try {
      const newReview = await triggerTestAudit();
      await loadData();
      setSelectedReview(newReview);
    } catch (err) {
      alert('Audit trigger failed: ' + err.message);
    } finally {
      setIsAuditing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      <Header onTriggerAudit={handleTriggerAudit} isAuditing={isAuditing} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <MetricsCards reviews={reviews} />

        {/* Audits Table */}
        <div className="border border-slate-800 rounded-2xl bg-slate-900/40 backdrop-blur-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Recent Pull Request Audits</h2>
              <p className="text-xs text-slate-400">Live feed of static analysis and AI threat detection</p>
            </div>
          </div>

          <div className="divide-y divide-slate-800/60">
            {reviews.length === 0 && !loading ? (
              <div className="p-12 text-center text-slate-500 text-sm">
                No reviews yet. Click "Run Test PR Audit" to simulate a security review.
              </div>
            ) : (
              reviews.map((rev) => (
                <div
                  key={rev.id}
                  onClick={() => setSelectedReview(rev)}
                  className="px-6 py-4 flex items-center justify-between hover:bg-slate-800/40 cursor-pointer transition duration-150"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-xl border ${
                      rev.security_risk_score > 70
                        ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                        : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    }`}>
                      {rev.security_risk_score > 70 ? (
                        <ShieldAlert className="w-5 h-5" />
                      ) : (
                        <CheckCircle2 className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-slate-200">
                          PR #{rev.pull_request}
                        </span>
                        <span className="text-xs font-mono text-slate-400">
                          {new Date(rev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-1 max-w-xl mt-0.5">
                        {rev.summary || 'Pending review...'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-xs font-mono text-slate-400">Risk Score</p>
                      <p className={`text-sm font-bold font-mono ${
                        rev.security_risk_score > 70 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        {rev.security_risk_score}/100
                      </p>
                    </div>

                    <div className="text-right hidden sm:block">
                      <p className="text-xs font-mono text-slate-400">Findings</p>
                      <p className="text-sm font-bold font-mono text-slate-300">
                        {rev.comments?.length || 0}
                      </p>
                    </div>

                    <ChevronRight className="w-4 h-4 text-slate-500" />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Detail Modal */}
      {selectedReview && (
        <ReviewModel
          review={selectedReview}
          onClose={() => setSelectedReview(null)}
        />
      )}
    </div>
  );
}