export async function onRequestGet(context) {
    const db = context.env.DB;

    if (!db) {
        return Response.json(
            { error: "Visitor counter database is not configured." },
            { status: 503, headers: { "Cache-Control": "no-store" } }
        );
    }

    try {
        const results = await db.batch([
            db.prepare(`
                CREATE TABLE IF NOT EXISTS site_stats (
                    stat_key TEXT PRIMARY KEY,
                    stat_value INTEGER NOT NULL DEFAULT 0
                )
            `),
            db.prepare(`
                INSERT INTO site_stats (stat_key, stat_value)
                VALUES ('site_visits', 1)
                ON CONFLICT(stat_key)
                DO UPDATE SET stat_value = stat_value + 1
            `),
            db.prepare(`
                SELECT stat_value AS visits
                FROM site_stats
                WHERE stat_key = 'site_visits'
            `)
        ]);

        const row = results[2]?.results?.[0];

        return Response.json(
            { visits: Number(row?.visits ?? 0) },
            {
                headers: {
                    "Cache-Control": "no-store"
                }
            }
        );
    } catch (error) {
        console.error("Visitor counter error:", error);

        return Response.json(
            { error: "Visitor counter unavailable." },
            { status: 500, headers: { "Cache-Control": "no-store" } }
        );
    }
}
