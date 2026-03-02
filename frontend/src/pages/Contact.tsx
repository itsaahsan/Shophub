import React from 'react';
import { Mail, Github } from 'lucide-react';

const Contact: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">
          Contact
        </h1>
        <p className="text-[15px] text-muted leading-relaxed">
          This Shophub demo was built to showcase full‑stack skills for top‑tier product teams:
          API design, authentication, payments, caching, and a polished UX.
        </p>
      </div>

      <div className="space-y-4 bg-white border border-border rounded-3xl p-6">
        <div className="flex items-center space-x-3">
          <Mail className="w-4 h-4 text-accent" />
          <div>
            <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Email</p>
            <p className="text-sm text-primary font-semibold">itsaahsan@gmail.com</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Github className="w-4 h-4 text-accent" />
          <div>
            <p className="text-xs font-extrabold uppercase tracking-widest text-muted">GitHub</p>
            <p className="text-sm text-primary font-semibold">github.com/itsaahsan</p>
          </div>
        </div>
      </div>

      <p className="text-xs text-muted">
        Tip for interviewers: explore the admin dashboard, Stripe‑style checkout flow,
        AI recommendations, and profile management to see how the system is structured end‑to‑end.
      </p>
    </div>
  );
};

export default Contact;

