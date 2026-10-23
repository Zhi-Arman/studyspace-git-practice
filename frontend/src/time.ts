export const timeOptions = Array.from(
  { length: 49 },
  (_, n) =>
    `${Math.floor(n / 2)
      .toString()
      .padStart(2, "0")}:${n % 2 ? "30" : "00"}`,
);
