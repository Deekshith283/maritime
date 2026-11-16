interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export default function AuthLayout({
  title,
  subtitle,
  children,
}: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-6">
      <div className="w-full max-w-md rounded-2xl border bg-background p-8 shadow-lg">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">{title}</h1>

          <p className="mt-2 text-muted-foreground">
            {subtitle}
          </p>
        </div>

        {children}
      </div>
    </div>
  );
}