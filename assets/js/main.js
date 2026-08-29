(function () {
  "use strict";

  var SECRET_PARAM = "v";
  var SECRET_VALUE = "1";

  // Single source of truth for the public "Launch Simulator" CTA.
  // Replace this with the production simulator URL when deploying.
  var SIMULATOR_URL = "https://amm-digital-health-project.onrender.com";

  function getLangPrefix() {
    var path = window.location.pathname;
    if (path.indexOf("/fr/") !== -1 || path.endsWith("/fr")) return "fr";
    if (path.indexOf("/ru/") !== -1 || path.endsWith("/ru")) return "ru";
    return "en";
  }

  function hasSecretParam() {
    return new URLSearchParams(window.location.search).get(SECRET_PARAM) === SECRET_VALUE;
  }

  function showRussianInNav() {
    return getLangPrefix() === "ru" || hasSecretParam();
  }

  function withSecretParam(url) {
    if (!hasSecretParam()) return url;
    var joiner = url.indexOf("?") === -1 ? "?" : "&";
    return url + joiner + SECRET_PARAM + "=" + SECRET_VALUE;
  }

  function buildLangUrl(lang) {
    var prefix = getLangPrefix();
    var page = window.location.pathname.split("/").pop() || "index.html";
    if (page === "" || page.indexOf(".") === -1) page = "index.html";

    var url;

    if (lang === "en") {
      if (prefix === "en") url = page === "index.html" ? "index.html" : page;
      else url = page === "index.html" ? "../index.html" : "../" + page;
    } else if (lang === "fr") {
      if (prefix === "fr") url = page;
      else if (prefix === "en") url = "fr/" + page;
      else url = "../fr/" + page;
    } else if (lang === "ru") {
      if (prefix === "ru") url = page;
      else if (prefix === "en") url = "ru/" + page;
      else url = "../ru/" + page;
    } else {
      return "#";
    }

    return withSecretParam(url);
  }

  function getDocsBase() {
    return getLangPrefix() === "en" ? "docs/" : "../docs/";
  }

  function initSpecDownload() {
    var link = document.querySelector("[data-spec-download]");
    if (!link) return;

    var lang = getLangPrefix();
    var files = {
      en: "AMM_Full_Specification_EN.docx",
      fr: "AMM_Full_Specification_FR.docx",
      ru: "AMM_Full_Specification_RU.docx",
    };

    link.setAttribute("href", getDocsBase() + files[lang]);
    link.setAttribute("download", "");
  }

  function initLangSwitch() {
    var switcher = document.querySelector(".lang-switch");
    if (!switcher) return;

    if (showRussianInNav()) {
      switcher.classList.add("ru-unlocked");
    }

    var current = getLangPrefix();
    var links = switcher.querySelectorAll("[data-lang]");
    links.forEach(function (link) {
      var lang = link.getAttribute("data-lang");
      link.setAttribute("href", buildLangUrl(lang));
      if (lang === current) {
        link.classList.add("active");
      }
    });
  }

  function initPreserveSecretOnNavLinks() {
    if (!hasSecretParam()) return;

    var scope = document.querySelector("header, main, footer");
    if (!scope) return;

    scope.querySelectorAll("a[href]").forEach(function (link) {
      var href = link.getAttribute("href");
      if (!href || href.charAt(0) === "#" || href.indexOf("://") !== -1 || href.indexOf("mailto:") === 0) {
        return;
      }
      if (href.indexOf(SECRET_PARAM + "=") !== -1) return;
      if (link.hasAttribute("download") || link.hasAttribute("data-spec-download")) return;
      if (href.indexOf("docs/") !== -1) return;
      link.setAttribute("href", withSecretParam(href));
    });
  }

  function initLightbox() {
    var images = document.querySelectorAll(
      ".hero-visual img, .gallery-item img, .content-image"
    );
    if (!images.length) return;

    var lightbox = document.createElement("div");
    lightbox.className = "lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-hidden", "true");
    lightbox.innerHTML =
      '<button type="button" class="lightbox-close" aria-label="Close">&times;</button>' +
      '<div class="lightbox-inner">' +
      '<img src="" alt="">' +
      '<p class="lightbox-caption"></p>' +
      "</div>";
    document.body.appendChild(lightbox);

    var lightboxImg = lightbox.querySelector("img");
    var lightboxCaption = lightbox.querySelector(".lightbox-caption");
    var closeBtn = lightbox.querySelector(".lightbox-close");

    function closeLightbox() {
      lightbox.classList.remove("open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.classList.remove("lightbox-open");
    }

    function openLightbox(img) {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || "";
      lightboxCaption.textContent = img.alt || "";
      lightboxCaption.style.display = img.alt ? "block" : "none";
      lightbox.classList.add("open");
      lightbox.setAttribute("aria-hidden", "false");
      document.body.classList.add("lightbox-open");
      closeBtn.focus();
    }

    images.forEach(function (img) {
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.addEventListener("click", function () {
        openLightbox(img);
      });
      img.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openLightbox(img);
        }
      });
    });

    closeBtn.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) closeLightbox();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && lightbox.classList.contains("open")) {
        closeLightbox();
      }
    });
  }

  function initMobileNav() {
    var toggle = document.querySelector(".menu-toggle");
    var nav = document.querySelector(".nav-links");
    if (!toggle || !nav) return;

    toggle.addEventListener("click", function () {
      nav.classList.toggle("open");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
      });
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1100) {
        nav.classList.remove("open");
      }
    });
  }

  function initSimulatorCta() {
    var links = document.querySelectorAll("[data-simulator]");
    if (!links.length) return;
    var lang = getLangPrefix();
    var joiner = SIMULATOR_URL.indexOf("?") === -1 ? "?" : "&";
    var url = SIMULATOR_URL + joiner + "lang=" + lang;
    links.forEach(function (link) {
      link.setAttribute("href", url);
    });
  }

  initSpecDownload();
  initLangSwitch();
  initPreserveSecretOnNavLinks();
  initSimulatorCta();
  initLightbox();
  initMobileNav();
})();
