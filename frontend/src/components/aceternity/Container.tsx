import type { PropsWithChildren } from "react";

export function Container({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen w-full">
      <div className="mx-auto w-full max-w-6xl px-4 py-10 md:px-6 md:py-14">{children}</div>
    </div>
  );
}
