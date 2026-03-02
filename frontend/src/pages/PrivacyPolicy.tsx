import React from 'react';

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">
          Privacy Policy
        </h1>
        <p className="text-sm text-muted">
          Last updated: March 2026
        </p>
      </div>

      <p className="text-[15px] text-muted leading-relaxed">
        Shophub is a demo e‑commerce experience built for portfolio and interview purposes.
        We do not process real payments or ship physical products. Any data you enter in this
        environment (such as email, name, or address) is used only to simulate a real shopping flow.
      </p>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary">Information We Collect</h2>
        <ul className="list-disc list-inside text-[15px] text-muted space-y-1">
          <li>Account details such as your name and email address.</li>
          <li>Demo order and cart information stored in our database.</li>
          <li>Basic analytics from your interactions with the site.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary">How We Use Your Data</h2>
        <p className="text-[15px] text-muted leading-relaxed">
          Data is used solely to power features like authentication, carts, orders, wishlists,
          and AI‑powered recommendations. This project is not intended for production use and
          should not be used to store sensitive personal information.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary">Contact</h2>
        <p className="text-[15px] text-muted leading-relaxed">
          If you are reviewing this project as part of a hiring process and have questions about
          the implementation, security, or data model, please reach out to the candidate directly.
        </p>
      </section>
    </div>
  );
};

export default PrivacyPolicy;

