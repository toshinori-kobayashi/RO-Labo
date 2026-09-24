/**
 * Config.local.js - RO-Lab local overrides for roBrowserLegacy (prototype)
 *
 * Server: rAthena Pre-Renewal, PACKETVER 20211103, login 54.65.172.5:6900
 * Assets: served locally by ro-glue from C:\Gravity\Ragnarok\data.grf (read-only)
 * Relay : ro-glue WebSocket -> TCP (allow-listed to 54.65.172.5:6900/6121/5121)
 *
 * NOTE: remoteClient is forced to the local glue so that NO asset is ever pulled
 *       from the upstream default (https://grf.robrowser.com/).
 */
window.ROConfigLocal = {
    development: false,
    enableConsole: true,
    packetDump: false,

    remoteClient: 'http://127.0.0.1:8000/client/',

    servers: [
        {
            display: 'RO PreRE',
            desc: 'Pre-Renewal Test Server',
            address: '54.65.172.5',
            port: 6900,
            version: 55,
            langtype: 2,                 // japan -> shift-jis / CP932 for user-facing text
            packetver: 20211103,         // must match rAthena PACKETVER
            renewal: false,              // Pre-Renewal
            worldMapSettings: { episode: 12 },
            packetKeys: false,           // rAthena keys are 0 for > 2018-03-07
            socketProxy: 'ws://127.0.0.1:8000/',
            remoteClient: 'http://127.0.0.1:8000/client/',
            adminList: [2000000]
        }
    ],

    skipIntro: true,          // no local drag&drop; everything via remoteClient
    skipServerList: false,    // Phase 2: we want to SEE the server list
    saveFiles: false,         // deprecated Chrome FS API; keep off

    // keep optional UIs off for the first E2E (fewer moving parts)
    enableCashShop: false,
    enableBank: false,
    enableCheckAttendance: false,
    enableMapName: false,
    enableRoulette: false,
    enableAchievements: false,
    enableDmgSuffix: false,
    loadLua: false
};
