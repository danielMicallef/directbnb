import { Suspense, ReactNode } from 'react';
import { LucideProps, icons } from 'lucide-react';

interface IconProps extends LucideProps {
  name: string;
  fallback?: ReactNode;
}

export function Icon({ name, fallback = null, ...props }: IconProps) {
  const LucideIcon = icons[name as keyof typeof icons];

  if (!LucideIcon) {
    return <>{fallback}</>;
  }

  return (
    <Suspense fallback={fallback}>
      <LucideIcon {...props} />
    </Suspense>
  );
}
