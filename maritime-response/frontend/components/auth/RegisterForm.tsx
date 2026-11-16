"use client";

export default function RegisterForm() {
  return (
    <form className="space-y-4">
      <div>
        <label className="mb-2 block text-sm font-medium">
          Full Name
        </label>

        <input
          className="w-full rounded-lg border px-3 py-2"
          placeholder="Full Name"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium">
          Email
        </label>

        <input
          type="email"
          className="w-full rounded-lg border px-3 py-2"
          placeholder="Email"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium">
          Password
        </label>

        <input
          type="password"
          className="w-full rounded-lg border px-3 py-2"
          placeholder="Password"
        />
      </div>

      <button
        type="submit"
        className="w-full rounded-lg bg-black py-2 text-white"
      >
        Register
      </button>
    </form>
  );
}