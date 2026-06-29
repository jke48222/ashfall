// ASHFALL — audio manager. HTMLAudio beds that crossfade Zenith <-> Fall, a
// transition whoosh, and narration. Must be started by a user gesture.
const A = 'assets/audio/';

function track(file, loop, target) {
  const a = new Audio(A + file);
  a.loop = loop;
  a.volume = 0;
  a.preload = 'auto';
  a._target = target;   // max volume
  a._goal = 0;          // current fade goal
  return a;
}

export class AudioManager {
  constructor() {
    this.started = false;
    this.state = 'ZENITH';
    this.zenith = [
      track('SFX_amb_crowd_market.mp3', true, 0.55),
      track('SFX_amb_water_fountain.mp3', true, 0.40),
    ];
    this.fall = [
      track('SFX_fall_fire_crackle.mp3', true, 0.55),
      track('SFX_fall_ash_wind.mp3', true, 0.55),
      track('SFX_fall_rumble_quake.mp3', true, 0.35),
    ];
    this.beds = [...this.zenith, ...this.fall];
    this.whoosh = new Audio(A + 'SFX_stinger_whoosh.mp3');
    this.intro = new Audio(A + 'VO_intro_chronomason.mp3');
    this.vo = {
      guide: new Audio(A + 'VO_guide_lucilla.mp3'),
      objective: new Audio(A + 'VO_objective_first.mp3'),
    };
  }

  start() {
    if (this.started) return;
    this.started = true;
    this.beds.forEach((a) => a.play().catch(() => {}));
    this.intro.volume = 0.95;
    this.intro.play().catch(() => {});
    this.setState(this.state);
  }

  setState(s) {
    this.state = s;
    const on = s === 'ZENITH' ? this.zenith : this.fall;
    const off = s === 'ZENITH' ? this.fall : this.zenith;
    on.forEach((a) => { a._goal = a._target; });
    off.forEach((a) => { a._goal = 0; });
    if (this.started) {
      try { this.whoosh.currentTime = 0; this.whoosh.volume = 0.7; this.whoosh.play(); } catch (e) { /* */ }
    }
  }

  say(name) {
    const a = this.vo[name];
    if (a) { try { a.volume = 0.95; a.currentTime = 0; a.play(); } catch (e) { /* */ } }
  }

  update(dt) {
    const k = Math.min(1, dt * 2.5);
    for (const a of this.beds) a.volume += (a._goal - a.volume) * k;
  }
}
