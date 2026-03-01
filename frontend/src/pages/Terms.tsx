import React from 'react';

const Terms: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">
          Terms of Service
        </h1>
        <p className="text-sm text-muted">
          Last updated: March 2026
        </p>
      </div>

      <p className="text-[15px] text-muted leading-relaxed">
        shophub is a non‑commercial demonstration project. By using this site you understand
        that it is intended for learning, experimentation, and interview evaluation only.
        No real purchases are fulfilled and no guarantees are provided.
      </p>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary">Use of the Service</h2>
        <ul className="list-disc list-inside text-[15px] text-muted space-y-1">
          <li>You agree not to enter real payment card numbers or highly sensitive data.</li>
          <li>You may create demo accounts and place demo orders to explore the UX.</li>
          <li>The author may reset or wipe demo data at any time.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary">No Warranty</h2>
        <p className="text-[15px] text-muted leading-relaxed">
          The project is provided “as is” without any warranties. It is not audited for production
          security or compliance and should not be treated as a production storefront.
        </p>
      </section>
    </div>
  );
};

export default Terms;

