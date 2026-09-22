function toIsoDate(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

function todayIsoDate() {
  return toIsoDate(new Date());
}

function currentMonthRange() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  const end = monthEnd < now ? monthEnd : now;
  return { start: toIsoDate(start), end: toIsoDate(end), today: toIsoDate(now) };
}
