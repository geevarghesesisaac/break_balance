const CACHE_NAME = "break-balance-v1";
const ASSETS = [
  "/",
  "/static/manifest.json",
  "/static/mug_favicon.ico",
  "/static/mug_icon-192.png",
  "/static/mug_icon-512.png"
];

const MESSAGES = [
  "Your coffee is missing you. Go say hi.",
  "Eyes tired? Even browsers blink sometimes.",
  "A short break can save a long mistake.",
  "Refill water. Reboot brain.",
  "Stretch a little. Your spine will thank you.",
  "Five minutes away can save fifty later.",
  "Even code compiles better after coffee.",
  "Have a break. Your brain deserves it.",
  "Stand up. Gravity misses you.",
  "Productivity loves small pauses.",
  "A calm mind works faster than a rushed one.",
  "Your chair called. It wants you back later.",
  "Good work needs good pauses.",
  "Blink. Breathe. Back to brilliance.",
  "Breaks are part of the job, not a break from it.",
  "A walk is cheaper than a chiropractor.",
  "Coffee first. Genius next.",
  "Rest is not a reward. It’s fuel.",
  "Your focus will thank you for a pause.",
  "Micro-break, macro-impact.",
  "Tea time is brain time.",
  "Step away. Come back sharper.",
  "Pause. Reset. Continue.",
  "A fresh mind fixes bugs faster.",
  "Small breaks, big clarity."
];

function isWithinWindow() {
  const now = new Date();
  const hour = now.getHours();
  return hour >= 12 && hour < 24;
}

function randomDelay() {
  const min = 2.5 * 60 * 60 * 1000;
  const max = 3.5 * 60 * 60 * 1000;
  return Math.floor(Math.random() * (max - min)) + min;
}

function scheduleNext() {
  if (!isWithinWindow()) return;

  const msg = MESSAGES[Math.floor(Math.random() * MESSAGES.length)];

  setTimeout(() => {
    if (isWithinWindow()) {
      self.registration.showNotification("Break Balance", {
        body: msg,
        icon: "/static/mug_icon-192.png"
      });
    }
    scheduleNext();
  }, randomDelay());
}

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
  scheduleNext();
});

self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
