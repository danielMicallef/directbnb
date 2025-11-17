import React from 'react';

interface SectionProps {
  id?: string;
  className?: string;
  title: string;
  children: React.ReactNode;
}

export function Section({ id, className, title, children }: SectionProps) {
  return (
    <section id={id} className={`py-20 ${className}`}>
      <div className="container mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-foreground">
          {title}
        </h2>
        {children}
      </div>
    </section>
  );
}
