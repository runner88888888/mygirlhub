"""
HTML templates for MyGirlHub static site generator.
All pages share the same design system.

EVERY HTML PAGE (homepage, video, category) MUST include:
- BODY_START (age gate + <body>) — used in render_homepage, render_video_page, render_category_page.
- GA_HEAD, HEAD_CSS, header_html(), footer_html() / sidebar as appropriate.
When adding a new page type, use BODY_START so the age gate is never left out.
"""

AFFILIATE_LINK = "https://t.amyfc.link/260715/779/0?bo=2779,2778,2777,2776,2775&po=6533&aff_sub5=SF_006OG000004lmDN"
BUNNY_LIBRARY  = "554827"
SITE_URL       = "https://mygirlhub.com"
SITE_NAME      = "Hot Camgirls Free – MyGirlHub"
GA_MEASUREMENT_ID = "G-EZ2QMXQVF2"

GA_HEAD = '''
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{ dataLayer.push(arguments); }}
  gtag('js', new Date());
  gtag('config', '{}');
</script>'''.format(GA_MEASUREMENT_ID, GA_MEASUREMENT_ID)

BANNER_HTML = '''<a href="{affiliate}" target="_blank" rel="noopener">
  <img src="https://www.imglnkx.com/779/003672A_MYFC_18_ALL_EN_30718_E.gif" alt="Watch Live Cam Girls Free" style="max-height:70px;display:block;">
</a>'''.format(affiliate=AFFILIATE_LINK)

WIDGET_HTML = '''<script src="https://crxcr2.com/cams-widget-ext/script?landing_id=260715&genders=f&providers=mfc&skin=1&containerAlignment=center&cols=1&rows=8&number=8&background=transparent&useFeed=1&animateFeed=1&smoothAnimation=1&ratio=1&verticalSpace=6px&horizontalSpace=0px&colorFilter=0&colorFilterStrength=0&AuxiliaryCSS=%0A&lang=en&token=7627ba70-1700-11f1-b290-61776f3048cd&api_key=0fbdaf6d973dcb2af01f87f20c9a16ba612468be61130e0e57f6bf9ca071fcc1"></script>'''

HEAD_CSS = '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#080808;
  --surface:#111111;
  --surface2:#191919;
  --surface3:#222222;
  --border:#282828;
  --border2:#333333;
  --accent:#ff2d55;
  --accent2:#ff6b35;
  --accent-glow:rgba(255,45,85,0.15);
  --text:#f2f2f2;
  --text2:#b0b0b0;
  --muted:#666;
  --sidebar-w:280px;
  --header-h:58px;
}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;overflow-x:hidden;}
a{color:inherit;text-decoration:none;}
img{display:block;}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}

/* ── HEADER ── */
header{
  background:rgba(8,8,8,0.95);
  backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  height:var(--header-h);
  position:sticky;top:0;z-index:200;
  display:flex;align-items:center;
  padding:0 20px 0 24px;
  gap:16px;
}
.logo{
  font-family:'Bebas Neue',sans-serif;
  font-size:26px;letter-spacing:3px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  flex-shrink:0;
}
.header-search{
  flex:1;max-width:460px;margin-left:8px;
  position:relative;
}
.header-search input{
  width:100%;
  background:var(--surface2);
  border:1px solid var(--border2);
  color:var(--text);
  font-family:'DM Sans',sans-serif;
  font-size:13px;
  padding:9px 14px 9px 36px;
  border-radius:6px;
  outline:none;
  transition:border-color 0.2s,box-shadow 0.2s;
}
.header-search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow);}
.header-search input::placeholder{color:var(--muted);}
.header-search svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);width:15px;height:15px;stroke:var(--muted);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;pointer-events:none;}
.header-nav{display:flex;align-items:center;gap:6px;margin-left:auto;}
.header-cta{
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-weight:600;font-size:13px;
  padding:9px 20px;border-radius:6px;
  letter-spacing:0.3px;
  white-space:nowrap;
  transition:opacity 0.2s,transform 0.1s;
  display:flex;align-items:center;gap:6px;
}
.header-cta:hover{opacity:0.88;transform:translateY(-1px);}
.live-badge{
  display:inline-flex;align-items:center;gap:5px;
  background:var(--surface2);border:1px solid var(--border2);
  color:var(--text2);font-size:12px;
  padding:7px 14px;border-radius:6px;
  white-space:nowrap;
}
.live-dot{width:7px;height:7px;background:#00e676;border-radius:50%;animation:pulse 1.5s infinite;flex-shrink:0;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:0.5;transform:scale(1.4);}}

/* ── BANNER ── */
.banner-wrap{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:7px 24px;
  display:flex;justify-content:center;align-items:center;
}

/* ── PAGE WRAPPER: full bleed ── */
.page-wrap{
  display:flex;
  width:100%;
  min-height:calc(100vh - var(--header-h));
}

/* ── MAIN CONTENT ── */
.main-content{
  flex:1;
  min-width:0;
  padding:18px 20px 32px 24px;
}

/* ── SIDEBAR ── */
.sidebar{
  width:var(--sidebar-w);
  min-width:var(--sidebar-w);
  flex-shrink:0;
  border-left:1px solid var(--border);
  padding:16px 14px;
  position:sticky;
  top:var(--header-h);
  height:calc(100vh - var(--header-h));
  overflow-y:auto;
  background:var(--surface);
}
.sidebar-section{margin-bottom:20px;}
.sidebar-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:15px;letter-spacing:2px;
  color:var(--muted);
  margin-bottom:12px;
  display:flex;align-items:center;gap:8px;
}

/* ── TOP BAR (count + sort) ── */
.content-topbar{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:14px;
  gap:12px;
  flex-wrap:wrap;
}
.content-topbar-left{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}
.content-topbar-right .pagination{margin-top:0;}
.content-topbar-right .page-btn{padding:5px 10px;font-size:12px;min-width:30px;}
.content-topbar-right .page-ellipsis{font-size:12px;padding:5px 2px;}
.section-label{
  font-family:'Bebas Neue',sans-serif;
  font-size:18px;letter-spacing:2px;
  color:var(--text2);
  display:flex;align-items:center;gap:10px;
}
.section-label::after{content:'';display:inline-block;width:32px;height:2px;background:linear-gradient(90deg,var(--accent),transparent);}
.count-badge{
  background:var(--surface2);border:1px solid var(--border2);
  color:var(--muted);font-size:11px;
  padding:3px 10px;border-radius:20px;
  font-weight:500;
}

/* ── PERFORMER FILTER ── */
.performer-filter{
  margin-bottom:16px;
  display:flex;flex-wrap:wrap;gap:5px;
}
.cat-pill{
  background:var(--surface2);border:1px solid var(--border);
  color:var(--muted);font-size:11px;font-weight:500;
  padding:5px 13px;border-radius:20px;
  transition:all 0.18s;cursor:pointer;
  white-space:nowrap;
}
.cat-pill:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-glow);}

/* ── VIDEO GRID ── */
/* Desktop: full remaining width, tight grid */
.video-grid{
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fill,minmax(190px,1fr));
}
@media(min-width:1400px){.video-grid{grid-template-columns:repeat(auto-fill,minmax(210px,1fr));}}
@media(min-width:1800px){.video-grid{grid-template-columns:repeat(auto-fill,minmax(220px,1fr));}}

/* ── VIDEO CARD ── */
.video-card{
  background:var(--surface);
  border-radius:7px;overflow:hidden;
  border:1px solid var(--border);
  transition:transform 0.18s,border-color 0.18s,box-shadow 0.18s;
  display:block;
  cursor:pointer;
}
.video-card:hover{
  transform:translateY(-3px);
  border-color:var(--accent);
  box-shadow:0 6px 24px rgba(255,45,85,0.12);
}
.thumb-wrap{position:relative;padding-top:56.25%;overflow:hidden;background:#000;}
.thumb-wrap img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}
.preview-gif{opacity:0;transition:opacity 0.25s;}
.video-card:hover .preview-gif{opacity:1;}
.card-duration{
  position:absolute;bottom:7px;right:8px;
  background:rgba(0,0,0,0.78);
  color:#fff;font-size:10px;font-weight:600;
  padding:2px 6px;border-radius:3px;
  pointer-events:none;
}
.play-overlay{
  position:absolute;inset:0;
  display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity 0.18s;

}
.video-card:hover .play-overlay{opacity:1;}
.play-circle{
  width:44px;height:44px;
  background:rgba(255,45,85,0.92);
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  backdrop-filter:blur(4px);
}
.play-circle svg{width:16px;height:16px;fill:#fff;margin-left:2px;}
.card-info{padding:9px 10px 11px;}
.card-title{
  font-size:12px;font-weight:500;line-height:1.35;
  margin-bottom:5px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
  color:var(--text);
}
.card-meta{display:flex;align-items:center;justify-content:space-between;gap:4px;}
.card-cat{
  font-size:10px;color:var(--accent);font-weight:600;
  text-transform:uppercase;letter-spacing:0.5px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  max-width:70%;
}
.card-views{font-size:10px;color:var(--muted);white-space:nowrap;flex-shrink:0;}

/* ── PAGINATION ── */
.pagination{
  display:flex;justify-content:center;align-items:center;
  gap:6px;margin-top:32px;flex-wrap:wrap;
}
.page-btn{
  background:#242424;border:1px solid #444;
  color:#ccc;font-size:13px;font-weight:500;
  padding:8px 14px;border-radius:6px;
  transition:all 0.18s;cursor:pointer;
  min-width:40px;text-align:center;
  text-decoration:none;display:inline-block;
}
.page-btn:hover{border-color:var(--accent);color:var(--accent);background:#1a0a0f;}
.page-btn.active{background:linear-gradient(135deg,var(--accent),var(--accent2));border-color:transparent;color:#fff;}
.page-btn.disabled{opacity:0.35;pointer-events:none;}
.page-ellipsis{color:var(--muted);padding:8px 4px;font-size:13px;}

/* ── VIDEO PAGE ── */
.video-page-grid{display:flex;gap:20px;align-items:flex-start;}
.video-page-main{flex:1;min-width:0;}
.video-embed-wrap{
  position:relative;padding-top:56.25%;
  background:#000;border-radius:8px;overflow:hidden;
  margin-bottom:18px;
}
.video-embed-wrap iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0;}
.video-title-large{
  font-family:'Bebas Neue',sans-serif;
  font-size:28px;letter-spacing:1px;
  margin-bottom:10px;line-height:1.1;
}
.video-meta-row{
  display:flex;align-items:center;gap:16px;
  margin-bottom:14px;
  flex-wrap:wrap;
}
.video-date{font-size:12px;color:var(--muted);}
.video-performer-link{
  font-size:12px;font-weight:600;color:var(--accent);
  text-transform:uppercase;letter-spacing:0.5px;
}
.video-tags{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:18px;}
.tag{
  background:var(--surface2);border:1px solid var(--border);
  color:var(--muted);font-size:11px;
  padding:4px 11px;border-radius:20px;
  transition:border-color 0.2s,color 0.2s;
}
.tag:hover{border-color:var(--accent);color:var(--accent);}
.affiliate-cta{
  display:flex;align-items:center;gap:16px;
  background:linear-gradient(135deg,rgba(255,45,85,0.08),rgba(255,107,53,0.08));
  border:1px solid rgba(255,45,85,0.35);
  border-radius:8px;padding:16px 20px;
  margin-bottom:24px;
  transition:background 0.2s,border-color 0.2s;
}
.affiliate-cta:hover{background:linear-gradient(135deg,rgba(255,45,85,0.15),rgba(255,107,53,0.15));border-color:var(--accent);}
.cta-icon{font-size:28px;flex-shrink:0;}
.cta-text strong{display:block;color:var(--accent);font-size:15px;font-weight:700;margin-bottom:2px;}
.cta-text span{color:var(--text2);font-size:12px;}
.video-desc{color:var(--text2);font-size:13px;line-height:1.75;margin-bottom:24px;}

/* ── SECTION TITLE (generic) ── */
.section-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:17px;letter-spacing:2px;
  color:var(--muted);
  margin-bottom:12px;
  display:flex;align-items:center;gap:10px;
}
.section-title::after{content:'';flex:1;height:1px;background:var(--border);}

/* ── BREADCRUMB ── */
.breadcrumb{
  font-size:12px;color:var(--muted);
  margin-bottom:16px;
  display:flex;align-items:center;gap:5px;
  flex-wrap:wrap;
}
.breadcrumb a{color:var(--muted);transition:color 0.2s;}
.breadcrumb a:hover{color:var(--text);}
.breadcrumb-sep{color:var(--border2);}

/* ── FOOTER ── */
footer{
  border-top:1px solid var(--border);
  padding:18px 24px;text-align:center;
  color:var(--muted);font-size:12px;
  margin-top:32px;
}
footer a{color:var(--muted);transition:color 0.2s;}
footer a:hover{color:var(--text);}

/* ── BACK TO TOP ── */
#back-to-top{
  position:fixed;bottom:24px;right:24px;
  width:40px;height:40px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  border-radius:50%;border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;
  transition:opacity 0.25s,transform 0.2s;
  z-index:150;
  box-shadow:0 4px 16px rgba(255,45,85,0.35);
}
#back-to-top.visible{opacity:1;pointer-events:auto;}
#back-to-top:hover{transform:translateY(-2px);}
#back-to-top svg{width:16px;height:16px;fill:none;stroke:#fff;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;}

/* ── HIDE zero views ── */
.card-views-zero{display:none;}

/* ── RESPONSIVE ── */
@media(max-width:1100px){
  .sidebar{display:none;}
  .video-grid{grid-template-columns:repeat(auto-fill,minmax(170px,1fr));}
}
@media(max-width:700px){
  .video-grid{grid-template-columns:repeat(2,1fr)!important;gap:7px;}
  .main-content{padding:12px;}
  header{padding:0 12px;}
  .header-search{display:none;}
  .live-badge{display:none;}
}
@media(max-width:420px){
  .video-grid{grid-template-columns:repeat(2,1fr)!important;}
  .video-title-large{font-size:22px;}
}

/* ── AGE GATE ── */
/* Body locked until verified — no nudity visible behind overlay */
body.age-locked{overflow:hidden!important;}
#age-gate{
  position:fixed;inset:0;
  background:#080808;
  z-index:999999;
  display:flex;align-items:center;justify-content:center;
  padding:20px;
  /* Fully opaque — content behind is invisible until dismissed */
}
#age-gate.hidden{display:none!important;}
.age-gate-box{
  background:#111;
  border:1px solid #333;
  border-radius:14px;
  padding:40px 36px;
  max-width:440px;width:100%;
  text-align:center;
  box-shadow:0 24px 80px rgba(0,0,0,0.95);
  position:relative;
}
.age-gate-logo{
  font-family:'Bebas Neue',sans-serif;
  font-size:32px;letter-spacing:3px;
  background:linear-gradient(135deg,#ff2d55,#ff6b35);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:4px;
}
.age-gate-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:20px;letter-spacing:2px;
  color:#f2f2f2;margin-bottom:14px;
}
.age-gate-text{
  font-size:13px;color:#888;
  margin-bottom:10px;line-height:1.6;
}
.age-gate-legal{
  font-size:11px;color:#555;
  margin-bottom:22px;line-height:1.55;
  border-top:1px solid #222;
  padding-top:12px;
}
.age-dob-label{
  font-size:11px;color:#666;
  margin-bottom:10px;letter-spacing:0.5px;
  text-transform:uppercase;
}
.age-gate-dob{
  display:flex;gap:8px;justify-content:center;
  margin-bottom:8px;flex-wrap:wrap;
}
.age-gate-dob select{
  background:#191919;border:1px solid #333;
  color:#f2f2f2;padding:11px 10px;
  border-radius:7px;font-size:14px;
  min-width:76px;outline:none;
  cursor:pointer;
  transition:border-color 0.2s;
  -webkit-appearance:none;appearance:none;
  text-align:center;
}
.age-gate-dob select:focus{border-color:#ff2d55;}
.age-gate-error{
  color:#ff2d55;font-size:12px;
  margin-bottom:14px;
  min-height:18px;
  display:none;
}
.age-gate-error.show{display:block;}
.age-gate-btns{
  display:flex;gap:10px;justify-content:center;flex-wrap:wrap;
  margin-top:16px;
}
.age-gate-btn{
  padding:13px 30px;border-radius:7px;
  font-size:14px;font-weight:600;
  cursor:pointer;border:none;
  transition:opacity 0.2s,transform 0.1s;
  font-family:'DM Sans',sans-serif;
  letter-spacing:0.3px;
}
.age-gate-btn.enter{
  background:linear-gradient(135deg,#ff2d55,#ff6b35);
  color:#fff;
}
.age-gate-btn.exit{
  background:#191919;color:#888;
  border:1px solid #333;
}
.age-gate-btn:hover{opacity:0.88;transform:translateY(-1px);}
.age-gate-18{
  display:inline-block;
  border:2px solid #ff2d55;color:#ff2d55;
  font-size:11px;font-weight:700;
  padding:2px 7px;border-radius:4px;
  margin-bottom:14px;letter-spacing:1px;
}
</style>'''

AGE_GATE = '''
<div id="age-gate">
  <div class="age-gate-box">
    <div class="age-gate-logo">MyGirlHub</div>
    <div class="age-gate-18">18+</div>
    <div class="age-gate-title">Age Verification Required</div>
    <p class="age-gate-text">This website contains sexually explicit material. Access is restricted to adults only.</p>
    <p class="age-dob-label">Enter your date of birth to continue</p>
    <div class="age-gate-dob">
      <select id="age-day" aria-label="Day of birth">
        <option value="">DD</option>
      </select>
      <select id="age-month" aria-label="Month of birth">
        <option value="">MM</option>
      </select>
      <select id="age-year" aria-label="Year of birth">
        <option value="">YYYY</option>
      </select>
    </div>
    <div class="age-gate-error" id="age-error" role="alert"></div>
    <div class="age-gate-btns">
      <button type="button" class="age-gate-btn enter" id="age-enter">Confirm I am 18+</button>
      <a href="https://www.google.com" class="age-gate-btn exit">Exit</a>
    </div>
    <p class="age-gate-legal">By entering this site you confirm you are 18 years of age or older and it is legal to view adult content in your jurisdiction. In compliance with Australian Online Safety Act 2021 and eSafety age assurance requirements, this site implements age verification before displaying explicit content.</p>
  </div>
</div>
<script>
(function(){
  var COOKIE = 'mgv2';
  var EXPIRE_DAYS = 30;

  function setCookie() {
    var exp = new Date();
    exp.setDate(exp.getDate() + EXPIRE_DAYS);
    var c = COOKIE + '=1; path=/; expires=' + exp.toUTCString() + '; SameSite=Lax';
    if (location.protocol === 'https:') c += '; Secure';
    document.cookie = c;
  }

  function getCookie() {
    var all = document.cookie.split(';');
    for (var i = 0; i < all.length; i++) {
      if (all[i].trim().indexOf(COOKIE + '=') === 0) return true;
    }
    return false;
  }

  function unlock() {
    var gate = document.getElementById('age-gate');
    if (gate) gate.classList.add('hidden');
    document.body.classList.remove('age-locked');
    document.body.style.overflow = '';
  }

  function showError(msg) {
    var el = document.getElementById('age-error');
    if (el) { el.textContent = msg; el.classList.add('show'); }
  }

  function clearError() {
    var el = document.getElementById('age-error');
    if (el) { el.textContent = ''; el.classList.remove('show'); }
  }

  // Lock body scroll while gate is showing
  document.body.classList.add('age-locked');

  // If already verified, unlock immediately
  if (getCookie()) { unlock(); return; }

  // Populate dropdowns
  var sd = document.getElementById('age-day');
  var sm = document.getElementById('age-month');
  var sy = document.getElementById('age-year');

  if (!sd || !sm || !sy) return;

  for (var d = 1; d <= 31; d++) {
    var o = document.createElement('option');
    o.value = d; o.text = (d < 10 ? '0' : '') + d;
    sd.appendChild(o);
  }

  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  for (var mi = 0; mi < 12; mi++) {
    var o = document.createElement('option');
    o.value = mi + 1; o.text = months[mi];
    sm.appendChild(o);
  }

  var thisYear = new Date().getFullYear();
  for (var yr = thisYear; yr >= thisYear - 110; yr--) {
    var o = document.createElement('option');
    o.value = yr; o.text = yr;
    sy.appendChild(o);
  }

  document.getElementById('age-enter').addEventListener('click', function() {
    clearError();

    var day  = parseInt(sd.value, 10);
    var mon  = parseInt(sm.value, 10);
    var year = parseInt(sy.value, 10);

    if (!day || !mon || !year) {
      showError('Please select your full date of birth.');
      return;
    }

    // Validate it is a real calendar date
    var testDate = new Date(year, mon - 1, day);
    if (
      testDate.getFullYear() !== year ||
      testDate.getMonth() !== mon - 1 ||
      testDate.getDate() !== day
    ) {
      showError('That date is not valid. Please check your date of birth.');
      return;
    }

    // Must be at least 18 full years old today
    var today = new Date();
    var age = today.getFullYear() - year;
    if (
      today.getMonth() < mon - 1 ||
      (today.getMonth() === mon - 1 && today.getDate() < day)
    ) {
      age--;
    }

    if (age < 18) {
      showError('You must be 18 or older to enter this site.');
      // Redirect underage users away
      setTimeout(function(){ window.location.href = 'https://www.google.com'; }, 1500);
      return;
    }

    // Verified — set cookie and unlock
    setCookie();
    unlock();
  });

  // Allow Enter key on selects to trigger confirm
  [sd, sm, sy].forEach(function(el) {
    el.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') document.getElementById('age-enter').click();
    });
  });

})();
</script>
'''

# Every HTML page must use this. The inline overflow:hidden is a failsafe before stylesheet loads.
BODY_START = '<body style="overflow:hidden">\n' + AGE_GATE

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def header_html(active_link="/"):
    return f'''<header>
  <a href="/" class="logo">MyGirlHub</a>
  <div class="header-search">
    <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="search" id="site-search" placeholder="Search performers, tags..." autocomplete="off">
  </div>
  <div class="header-nav">
    <span class="live-badge"><span class="live-dot"></span>Live Now</span>
    <a href="{AFFILIATE_LINK}" target="_blank" rel="noopener" class="header-cta">🔴 Watch Live Free</a>
  </div>
</header>
<div class="banner-wrap">{BANNER_HTML}</div>'''

def sidebar_html():
    return f'''<aside class="sidebar">
  <div class="sidebar-section">
    <div class="sidebar-title"><span class="live-dot"></span>&nbsp;Live Girls</div>
    {WIDGET_HTML}
  </div>
</aside>'''

def footer_html():
    return '''<footer>
  <p>© 2026 MyGirlHub.com &nbsp;·&nbsp;
  <a href="/content-removal.html">DMCA / Content Removal</a> &nbsp;·&nbsp;
  <a href="/privacy.html">Privacy Policy</a> &nbsp;·&nbsp;
  <a href="/2257.html">18 U.S.C. 2257</a> &nbsp;·&nbsp;
  All models are 18+ &nbsp;·&nbsp;
  <a href="https://www.freeones.com/" target="_blank" rel="noopener">FreeOnes</a>
  </p>
</footer>'''

def video_card_html(v, priority=False):
    slug  = v['slug']
    cdn   = v['cdn']
    guid  = v['guid']
    title = esc(v['title'])
    perf  = esc(v['performer'])
    views = v.get('views', 0)
    cat_url = f"/category/{v['performer_slug']}/"
    views_fmt = f"{views:,}" if isinstance(views, int) and views > 0 else ""
    views_html = f'<span class="card-views">{views_fmt} views</span>' if views_fmt else ''
    fetch_attr = ' fetchpriority="high"' if priority else ' loading="lazy"'
    # preview.webp is auto-generated by Bunny Stream for every video
    preview_url = f"https://{cdn}/{guid}/preview.webp"
    return f'''<a class="video-card" href="/videos/{slug}/">
  <div class="thumb-wrap">
    <img src="{preview_url}" alt="{title}"{fetch_attr} width="320" height="180">
    <div class="play-overlay"><div class="play-circle"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div></div>
  </div>
  <div class="card-info">
    <div class="card-title">{title}</div>
    <div class="card-meta">
      <a class="card-cat" href="{cat_url}">{perf}</a>
      {views_html}
    </div>
  </div>
</a>'''

def schema_video(v):
    import json as _json
    return f'''<script type="application/ld+json">
{_json.dumps({
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": v['title'],
  "description": v.get('description', v['title']),
  "thumbnailUrl": f"https://{v['cdn']}/{v['guid']}/preview.webp",
  "uploadDate": v['date'],
  "embedUrl": f"https://player.mediadelivery.net/embed/{BUNNY_LIBRARY}/{v['guid']}",
  "author": {"@type": "Person", "name": v['performer']}
}, indent=2)}
</script>'''

# ── PAGINATION HELPER ──────────────────────────────────────────────────
PER_PAGE = 25

def _pagination_html(current_page, total_pages, base_url="/"):
    """Generate pagination HTML. page 1 = base_url, page N = base_url + page/N/"""
    if total_pages <= 1:
        return ""

    def page_url(p):
        if p == 1:
            return base_url
        return f"{base_url}page/{p}/"

    parts = []
    # Prev
    if current_page > 1:
        parts.append(f'<a class="page-btn" href="{page_url(current_page-1)}">&#8249; Prev</a>')
    else:
        parts.append('<span class="page-btn disabled">&#8249; Prev</span>')

    # Page numbers with ellipsis
    def add_page(p):
        if p == current_page:
            parts.append(f'<span class="page-btn active">{p}</span>')
        else:
            parts.append(f'<a class="page-btn" href="{page_url(p)}">{p}</a>')

    if total_pages <= 7:
        for p in range(1, total_pages + 1):
            add_page(p)
    else:
        add_page(1)
        if current_page > 3:
            parts.append('<span class="page-ellipsis">…</span>')
        start = max(2, current_page - 1)
        end   = min(total_pages - 1, current_page + 1)
        for p in range(start, end + 1):
            add_page(p)
        if current_page < total_pages - 2:
            parts.append('<span class="page-ellipsis">…</span>')
        add_page(total_pages)

    # Next
    if current_page < total_pages:
        parts.append(f'<a class="page-btn" href="{page_url(current_page+1)}">Next &#8250;</a>')
    else:
        parts.append('<span class="page-btn disabled">Next &#8250;</span>')

    return f'<div class="pagination">{"".join(parts)}</div>'


# ── HOMEPAGE ──────────────────────────────────────────────────────────
def render_homepage(videos, categories, page=1):
    """Render homepage for a given page number (1-indexed)."""
    total = len(videos)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    page_videos = videos[start:start + PER_PAGE]

    cards = '\n'.join(video_card_html(v, priority=(i < 6)) for i, v in enumerate(page_videos))

    cat_pills = '\n'.join(
        f'<a class="cat-pill" href="/category/{c["slug"]}/">{esc(c["name"])} ({c["count"]})</a>'
        for c in sorted(categories, key=lambda x: -x['count'])[:40]
    )

    pagination = _pagination_html(page, total_pages, "/")

    page_suffix = f" – Page {page} of {total_pages}" if page > 1 else ""
    page_title = f"Hot Camgirls Free – Watch Free Cam Videos | MyGirlHub{page_suffix}"
    canonical  = f"{SITE_URL}/" if page == 1 else f"{SITE_URL}/page/{page}/"

    # rel prev/next for Google pagination crawling
    prev_link = ""
    next_link = ""
    if page > 1:
        prev_url = f"{SITE_URL}/" if page == 2 else f"{SITE_URL}/page/{page-1}/"
        prev_link = f'<link rel="prev" href="{prev_url}">'
    if page < total_pages:
        next_link = f'<link rel="next" href="{SITE_URL}/page/{page+1}/">'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<meta name="description" content="Watch free cam girl videos from the hottest live performers. New videos added daily. MyGirlHub – your free camgirl video hub.">
<link rel="canonical" href="{canonical}">
{prev_link}
{next_link}
<meta property="og:title" content="Hot Camgirls Free – MyGirlHub">
<meta property="og:description" content="Watch free cam girl videos from the hottest performers.">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
{GA_HEAD}
{HEAD_CSS}
</head>
{BODY_START}
{header_html()}
<div class="page-wrap">
<div class="main-content">

  <!-- Performer filter -->
  <div class="performer-filter" id="perf-filter">
    {cat_pills}
  </div>

  <!-- Top bar -->
  <div class="content-topbar">
    <div class="content-topbar-left">
      <div class="section-label">Latest Videos</div>
      <span class="count-badge">Showing {start+1}–{min(start+PER_PAGE, total)} of {total}</span>
    </div>
    <div class="content-topbar-right">
      {pagination}
    </div>
  </div>

  <!-- Grid -->
  <div class="video-grid" id="grid">{cards}</div>

  <!-- Pagination bottom -->
  {pagination}

</div>
{sidebar_html()}
</div>
{footer_html()}
<button id="back-to-top" aria-label="Back to top">
  <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
</button>
<script>
(function(){{
  // Header search → filter cards on current page
  var inp = document.getElementById('site-search');
  if(inp){{
    var cards = Array.from(document.querySelectorAll('.video-card'));
    inp.addEventListener('input', function(){{
      var q = this.value.toLowerCase().trim();
      cards.forEach(function(c){{
        c.style.display = (!q || c.textContent.toLowerCase().includes(q)) ? '' : 'none';
      }});
    }});
  }}
  // Back to top
  var btn = document.getElementById('back-to-top');
  if(btn){{
    window.addEventListener('scroll', function(){{
      btn.classList.toggle('visible', window.scrollY > 400);
    }}, {{passive:true}});
    btn.addEventListener('click', function(){{
      window.scrollTo({{top:0, behavior:'smooth'}});
    }});
  }}
}})();
</script>
</body>
</html>'''


# ── VIDEO PAGE ────────────────────────────────────────────────────────
def render_video_page(v, all_videos=None):
    tags_html = ''.join(
        f'<a class="tag" href="/category/{v["performer_slug"]}/">{esc(t)}</a>'
        for t in v.get('tags', [])
    )
    desc = esc(v.get('description', v['title']))

    # Related videos: same performer, exclude self, max 12
    related_section = ""
    if all_videos:
        related = [x for x in all_videos if x['performer_slug'] == v['performer_slug'] and x['slug'] != v['slug']][:12]
        if related:
            related_cards = '\n'.join(video_card_html(r) for r in related)
            related_section = f'<div class="section-title">More {esc(v["performer"])} Videos</div><div class="video-grid">{related_cards}</div>'

    views = v.get('views', 0)
    views_html = f'<span class="video-date">{views:,} views</span>' if isinstance(views, int) and views > 0 else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(v['title'])} | MyGirlHub</title>
<meta name="description" content="Watch {esc(v['performer'])} free cam video – {esc(v['title'])}. Stream now on MyGirlHub.">
<link rel="canonical" href="{SITE_URL}/videos/{v['slug']}/">
<meta property="og:title" content="{esc(v['title'])}">
<meta property="og:description" content="Watch {esc(v['performer'])} free cam video on MyGirlHub.">
<meta property="og:image" content="https://{v['cdn']}/{v['guid']}/preview.webp">
<meta property="og:url" content="{SITE_URL}/videos/{v['slug']}/">
<meta property="og:type" content="video.other">
{schema_video(v)}
{GA_HEAD}
{HEAD_CSS}
</head>
{BODY_START}
{header_html()}
<div class="page-wrap">
<div class="main-content">
  <div class="breadcrumb">
    <a href="/">Home</a>
    <span class="breadcrumb-sep">/</span>
    <a href="/category/{v['performer_slug']}/">{esc(v['performer'])}</a>
    <span class="breadcrumb-sep">/</span>
    <span>{esc(v['title'])}</span>
  </div>

  <div class="video-embed-wrap">
    <iframe src="https://player.mediadelivery.net/embed/{BUNNY_LIBRARY}/{v['guid']}?autoplay=false&loop=false&muted=false&preload=true&responsive=true"
      loading="lazy"
      style="border:0;position:absolute;top:0;height:100%;width:100%;"
      allow="accelerometer;gyroscope;autoplay;encrypted-media;picture-in-picture;"
      allowfullscreen="true"></iframe>
  </div>

  <h1 class="video-title-large">{esc(v['title'])}</h1>

  <div class="video-meta-row">
    <a class="video-performer-link" href="/category/{v['performer_slug']}/">{esc(v['performer'])}</a>
    <span class="video-date">{v.get('date','')}</span>
    {views_html}
  </div>

  <div class="video-tags">{tags_html}</div>

  <a href="{AFFILIATE_LINK}" target="_blank" rel="noopener" class="affiliate-cta">
    <span class="cta-icon">🔴</span>
    <div class="cta-text">
      <strong>Watch {esc(v['performer'])} LIVE now — Get 100 FREE Tokens!</strong>
      <span>She's online right now on MyFreeCams</span>
    </div>
  </a>

  <p class="video-desc">{desc}</p>

  {related_section}
</div>
{sidebar_html()}
</div>
{footer_html()}
<button id="back-to-top" aria-label="Back to top">
  <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
</button>
<script>
(function(){{
  var btn = document.getElementById('back-to-top');
  if(!btn) return;
  window.addEventListener('scroll', function(){{ btn.classList.toggle('visible', window.scrollY > 400); }}, {{passive:true}});
  btn.addEventListener('click', function(){{ window.scrollTo({{top:0, behavior:'smooth'}}); }});
}})();
</script>
</body>
</html>'''


# ── CATEGORY PAGE ─────────────────────────────────────────────────────
def render_category_page(performer, performer_slug, videos, page=1):
    total = len(videos)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    page_videos = videos[start:start + PER_PAGE]

    cards = '\n'.join(video_card_html(v, priority=(i < 6)) for i, v in enumerate(page_videos))
    pagination = _pagination_html(page, total_pages, f"/category/{performer_slug}/")
    canonical  = f"{SITE_URL}/category/{performer_slug}/" if page == 1 else f"{SITE_URL}/category/{performer_slug}/page/{page}/"

    page_suffix = f" – Page {page} of {total_pages}" if page > 1 else ""
    page_title_str = f"{esc(performer)} Free Cam Videos – Watch {esc(performer)} Live | MyGirlHub{page_suffix}"
    meta_desc = f"Watch {total} free cam videos from {esc(performer)} on MyGirlHub. Stream {esc(performer)}'s best performances free – updated regularly."

    prev_link = ""
    next_link = ""
    if page > 1:
        prev_url = f"{SITE_URL}/category/{performer_slug}/" if page == 2 else f"{SITE_URL}/category/{performer_slug}/page/{page-1}/"
        prev_link = f'<link rel="prev" href="{prev_url}">'
    if page < total_pages:
        next_link = f'<link rel="next" href="{SITE_URL}/category/{performer_slug}/page/{page+1}/">'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title_str}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{canonical}">
{prev_link}
{next_link}
<meta property="og:title" content="{esc(performer)} Free Cam Videos | MyGirlHub">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
{GA_HEAD}
{HEAD_CSS}
</head>
{BODY_START}
{header_html()}
<div class="page-wrap">
<div class="main-content">
  <div class="breadcrumb">
    <a href="/">Home</a>
    <span class="breadcrumb-sep">/</span>
    <span>{esc(performer)}</span>
  </div>

  <div class="content-topbar">
    <div class="content-topbar-left">
      <div class="section-label">{esc(performer)}</div>
      <span class="count-badge">{total} video{"s" if total != 1 else ""}</span>
    </div>
  </div>

  <div class="video-grid">{cards}</div>
  {pagination}
</div>
{sidebar_html()}
</div>
{footer_html()}
<button id="back-to-top" aria-label="Back to top">
  <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
</button>
<script>
(function(){{
  var btn = document.getElementById('back-to-top');
  if(!btn) return;
  window.addEventListener('scroll', function(){{ btn.classList.toggle('visible', window.scrollY > 400); }}, {{passive:true}});
  btn.addEventListener('click', function(){{ window.scrollTo({{top:0, behavior:'smooth'}}); }});
}})();
</script>
</body>
</html>'''


# ── SITEMAP & ROBOTS ──────────────────────────────────────────────────
def render_sitemap(videos):
    urls = [f'''  <url>
    <loc>{SITE_URL}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>''']
    seen_cats = set()
    for v in videos:
        urls.append(f'''  <url>
    <loc>{SITE_URL}/videos/{v['slug']}/</loc>
    <lastmod>{v['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
        if v['performer_slug'] not in seen_cats:
            seen_cats.add(v['performer_slug'])
            urls.append(f'''  <url>
    <loc>{SITE_URL}/category/{v['performer_slug']}/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''

def render_robots():
    return f'''User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml'''
