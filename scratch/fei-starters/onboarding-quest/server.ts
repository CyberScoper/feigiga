// Bun + Hono onboarding-сервер для первокурсников FEI STU
import { Hono } from "hono";
import { serveStatic } from "hono/bun";

const app = new Hono();

const PROGRAMS = [
  "Aplikovaná informatika",
  "Robotika a kybernetika",
  "Elektronické systémy a návrh čipov",
  "Informačné a komunikačné technológie",
  "Digitálne technológie",
  "Elektroenergetika",
  "Elektrotechnika",
  "Inteligentné technológie a automobilová mechatronika",
  "Jadrové a fyzikálne inžinierstvo",
];

// Хардкод данных из ресёрча FEI STU 2025/26
const DATA = {
  isic: { price: 24, note: "ISIC karta (validná na MHD a stravu)" },
  transcard: { price: 3.08, note: "TransCard pre dotovanú stravu" },
  ids_bk: { price: 29.10, note: "IDS BK predplatné 30 dní, zóny 100+101" },
  dorms: ["Mladosť", "Akadémia", "Družba", "Nikosa Belojanisa", "Jura Hronca", "Svoradov"],
};

type Step = { id: string; title: string; due: string; price?: number; note: string };

function plan(name: string, surname: string, program: string, fromHome: string): Step[] {
  const t = (s: string) => s; // i18n hook
  return [
    { id: "zapis", title: t("Zápis na štúdium"), due: "2025-08-25", note: "Online + osobná účasť. Doniesť maturitné vysvedčenie." },
    { id: "isic", title: t("Vybaviť ISIC kartu"), due: "2025-09-05", price: DATA.isic.price, note: DATA.isic.note },
    { id: "sd", title: t("Žiadosť o ŠD"), due: "2025-08-15", note: `6 ŠD STU: ${DATA.dorms.join(", ")}. Prioritu má vzdialenosť ${fromHome || "<zadaj domov>"}.` },
    { id: "transcard", title: t("TransCard pre stravu"), due: "2025-09-15", price: DATA.transcard.price, note: DATA.transcard.note },
    { id: "ids", title: t("IDS BK predplatné"), due: "2025-09-15", price: DATA.ids_bk.price, note: DATA.ids_bk.note },
    { id: "imatr", title: t("Imatrikulácia"), due: "2025-10-15", note: `Slávnostná, ${program}.` },
    { id: "sem_start", title: t("Začiatok semestra"), due: "2025-09-22", note: `${name} ${surname}, prvý týždeň prednášok.` },
  ];
}

app.get("/", c => c.redirect("/static/index.html"));
app.use("/static/*", serveStatic({ root: "./" }));

app.get("/api/programs", c => c.json(PROGRAMS));
app.get("/api/data", c => c.json(DATA));

app.post("/plan", async c => {
  const b = await c.req.json();
  const { name = "", surname = "", program = "", fromHome = "" } = b;
  const steps = plan(name, surname, program, fromHome);
  const total = steps.reduce((s, x) => s + (x.price || 0), 0);
  return c.json({ steps, total_eur: Math.round(total * 100) / 100 });
});

app.get("/calendar.ics", c => {
  // принимаем query: ?name=...&surname=...&program=...&fromHome=...
  const q = c.req.query();
  const steps = plan(q.name || "", q.surname || "", q.program || "", q.fromHome || "");
  const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//fei-starter//onboarding//SK"];
  for (const s of steps) {
    const d = s.due.replace(/-/g, "");
    lines.push("BEGIN:VEVENT");
    lines.push(`UID:${s.id}@fei-starter`);
    lines.push(`DTSTART;VALUE=DATE:${d}`);
    lines.push(`DTEND;VALUE=DATE:${d}`);
    lines.push(`SUMMARY:${s.title}${s.price ? ` (${s.price} €)` : ""}`);
    lines.push(`DESCRIPTION:${s.note.replace(/\n/g, " ")}`);
    lines.push("END:VEVENT");
  }
  lines.push("END:VCALENDAR");
  return new Response(lines.join("\r\n"), {
    headers: { "content-type": "text/calendar; charset=utf-8", "content-disposition": "attachment; filename=onboarding.ics" },
  });
});

const port = Number(process.env.PORT || 3000);
console.log(`onboarding-quest на http://localhost:${port}`);
export default { port, fetch: app.fetch };
