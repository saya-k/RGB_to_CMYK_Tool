from __future__ import annotations

import json
import os
import re
import threading
import webbrowser
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from convert_rgb_to_cmyk import (
    INPUT_DIR,
    OUTPUT_DIR,
    SUPPORTED_EXTENSIONS,
    ensure_directories,
    run_conversion,
    unique_path,
)
from icc_profiles import (
    CUSTOM_PROFILE_DIR,
    DEFAULT_PROFILE_ID,
    PRESET_PROFILES,
    ensure_profile_dirs,
    resolve_preset_path,
)
from source_rgb_profiles import (
    DEFAULT_DITHERING,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_RENDERING_INTENT,
    DEFAULT_SOURCE_RGB_ID,
    OUTPUT_FORMATS,
    RENDERING_INTENTS,
    SOURCE_RGB_CUSTOM_DIR,
    SOURCE_RGB_PRESET_DIR,
    SOURCE_RGB_PROFILES,
    ensure_source_profile_dirs,
    output_format_by_id,
    rendering_intent_value,
    resolve_source_profile_path,
)


HOST = "127.0.0.1"
PORT = 0
MAX_UPLOAD_BYTES = 600 * 1024 * 1024


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RGB to CMYK Tool</title>
  <style>
    :root {
      --ink: #061733;
      --muted: #496079;
      --line: #c8d7ea;
      --teal: #135f66;
      --teal-dark: #0c464b;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --soft: #f8fbff;
      --warn-bg: #fff8e6;
      --danger: #bc3a13;
      --ok: #008f5a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: #fff;
      color: var(--ink);
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
    }
    main {
      width: min(1160px, calc(100vw - 48px));
      margin: 22px auto 40px;
    }
    h1, h2 {
      margin: 0 0 18px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    h1 {
      color: var(--teal);
      font-size: 30px;
      font-weight: 900;
      margin-bottom: 8px;
    }
    h2 { font-size: 21px; }
    .lead {
      max-width: 780px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.65;
      margin: 0 0 22px;
    }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 32px;
      align-items: start;
    }
    .card {
      background: var(--panel);
      border: 1px solid #e0e8f0;
      border-radius: 8px;
      padding: 32px;
      box-shadow: 0 10px 24px rgba(16, 37, 62, 0.10);
    }
    .side-card {
      position: sticky;
      top: 18px;
      padding: 32px;
    }
    .section {
      padding: 0 0 28px;
      border-bottom: 0;
    }
    .section + .section { padding-top: 8px; }
    .section:last-child { padding-bottom: 0; }
    .tabs {
      display: grid;
      grid-template-columns: 1fr 1fr;
      border-bottom: 1px solid #dce5ef;
      margin-bottom: 18px;
    }
    .tab {
      height: 42px;
      border: 0;
      border-bottom: 3px solid transparent;
      border-radius: 0;
      background: transparent;
      color: #12304b;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
    }
    .tab.active {
      color: var(--teal);
      border-bottom-color: var(--teal);
    }
    .label {
      display: block;
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 10px;
    }
    select {
      width: 100%;
      height: 46px;
      padding: 0 14px;
      border: 1px solid #c6d5e6;
      border-radius: 7px;
      background: #fff;
      color: var(--ink);
      font-size: 15px;
    }
    select:focus { outline: 2px solid rgba(19, 95, 102, .18); border-color: var(--teal); }
    .factor-options {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }
    .factor-option {
      height: 44px;
      border: 1px solid transparent;
      border-radius: 8px;
      background: #f3f5fa;
      color: #6d7a91;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(20, 38, 55, .07);
    }
    .factor-option.active {
      border-color: #2f75ff;
      background: #f7f8ff;
      color: #2f65ff;
      box-shadow: 0 0 0 2px rgba(47, 117, 255, .12);
    }
    .factor-option:focus-visible {
      outline: 2px solid rgba(47, 117, 255, .28);
      outline-offset: 2px;
    }
    .profile-card {
      margin-top: 16px;
      padding: 22px;
      border: 1px solid #bdd2e5;
      border-radius: 8px;
      background: var(--soft);
    }
    .profile-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .profile-title {
      font-size: 20px;
      font-weight: 800;
      line-height: 1.35;
    }
    .badge {
      flex: 0 0 auto;
      padding: 5px 9px;
      border-radius: 999px;
      background: var(--teal);
      color: #fff;
      font-size: 12px;
      font-weight: 800;
    }
    .desc {
      margin: 0 0 16px;
      color: #173251;
      line-height: 1.7;
      font-size: 14px;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(180px, 1fr));
      gap: 12px;
    }
    .meta {
      min-height: 72px;
      padding: 12px 14px;
      border-radius: 7px;
      background: #fff;
      border: 1px solid #edf2f7;
    }
    .meta small {
      display: block;
      color: #35516d;
      margin-bottom: 7px;
      font-weight: 700;
    }
    .meta strong {
      display: block;
      color: #001a35;
      line-height: 1.35;
    }
    .profile-warning {
      margin-top: 12px;
      color: #8a4300;
      font-size: 13px;
      line-height: 1.55;
    }
    .setting-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(220px, 1fr));
      gap: 18px;
      align-items: start;
    }
    .field-note {
      margin-top: 7px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .checkbox-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 8px;
      font-weight: 800;
    }
    .checkbox-row input {
      width: 17px;
      height: 17px;
      accent-color: var(--teal);
    }
    .dropzone {
      min-height: 180px;
      border: 2px dashed var(--line);
      border-radius: 8px;
      background: #f9fbfe;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 24px;
      cursor: pointer;
      transition: border-color .16s ease, background .16s ease;
    }
    .dropzone.compact { min-height: 144px; }
    .dropzone.dragover {
      border-color: var(--teal);
      background: #eef8f8;
    }
    .plus {
      font-size: 54px;
      line-height: 1;
      color: #8fa1b8;
      margin-bottom: 12px;
      font-weight: 200;
    }
    .primary-text {
      font-weight: 700;
      color: #021832;
      margin-bottom: 8px;
    }
    .secondary-text {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.65;
    }
    input[type="file"] { display: none; }
    .hidden { display: none; }
    .file-list {
      margin: 16px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
      max-height: 180px;
      overflow: auto;
    }
    .file-list li {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      border: 1px solid #dde7f1;
      border-radius: 6px;
      background: #fbfdff;
      color: #21364f;
      font-size: 14px;
    }
    .actions {
      display: flex;
      align-items: stretch;
      justify-content: flex-start;
      gap: 14px;
      margin-top: 18px;
      flex-direction: column;
      flex-wrap: wrap;
    }
    .button {
      width: 100%;
      min-width: 0;
      height: 50px;
      border: 0;
      border-radius: 6px;
      background: var(--teal);
      color: #fff;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
    }
    .button:hover { background: var(--teal-dark); }
    .button:disabled {
      cursor: not-allowed;
      background: #a9bac8;
    }
    .status {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
      min-height: 22px;
    }
    .result {
      margin-top: 18px;
      display: none;
      border: 1px solid #dbe6ef;
      border-radius: 8px;
      overflow: hidden;
    }
    .result.visible { display: block; }
    .summary {
      display: grid;
      grid-template-columns: repeat(5, minmax(80px, 1fr));
      gap: 0;
      background: #fff;
    }
    .summary div {
      padding: 14px;
      border-right: 1px solid #edf1f5;
    }
    .summary div:last-child { border-right: 0; }
    .summary strong {
      display: block;
      font-size: 22px;
      margin-bottom: 4px;
    }
    .summary span {
      color: var(--muted);
      font-size: 13px;
    }
    .notice {
      padding: 13px 14px;
      border-top: 1px solid #edf1f5;
      background: var(--warn-bg);
      color: #794000;
      font-size: 14px;
    }
    .error { color: var(--danger); font-weight: 700; }
    .ok { color: var(--ok); font-weight: 700; }
    .about-card {
      margin-top: 26px;
      padding: 20px;
      border: 1px solid #bdd2e5;
      border-radius: 8px;
      background: #fbfdff;
      color: #243a55;
      line-height: 1.55;
      font-size: 14px;
    }
    .about-card strong {
      display: block;
      color: var(--ink);
      font-size: 16px;
      margin-bottom: 10px;
    }
    @media (max-width: 720px) {
      main { width: min(100vw - 28px, 640px); margin-top: 18px; }
      h1 { font-size: 25px; }
      .workspace { grid-template-columns: 1fr; gap: 18px; }
      .card, .side-card { padding: 22px; }
      .side-card { position: static; }
      .tabs { grid-template-columns: 1fr; }
      .setting-grid { grid-template-columns: 1fr; }
      .meta-grid { grid-template-columns: 1fr; }
      .summary { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
      .summary div { border-bottom: 1px solid #edf1f5; }
      .button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <h1>Professional RGB to CMYK Converter For Printing</h1>
    <p class="lead">
      Built for professional printing, this local RGB to CMYK converter uses built-in presets or custom ICC profiles
      to convert images with preview reports and print-ready output.
    </p>
    <div class="workspace">
      <div class="card">
        <section class="section">
          <h2>Upload Image</h2>
          <section id="dropzone" class="dropzone" tabindex="0" role="button" aria-label="Select images">
            <div>
              <div class="plus">+</div>
              <div class="primary-text">Drag and drop your image here, or click to select</div>
              <div class="secondary-text">Supported formats: JPG, JPEG, PNG, TIFF, TIF, WebP</div>
            </div>
          </section>
          <input id="fileInput" type="file" accept=".jpg,.jpeg,.png,.tif,.tiff,.webp,image/jpeg,image/png,image/tiff,image/webp" multiple>
          <ul id="fileList" class="file-list"></ul>
        </section>

        <section class="section">
          <h2>ICC Profile</h2>
          <div class="tabs">
            <button id="presetTab" class="tab active" type="button">Preset Profiles</button>
            <button id="customTab" class="tab" type="button">Custom Profile</button>
          </div>
          <div id="presetPanel">
            <label class="label" for="profileSelect">Select Profile</label>
            <select id="profileSelect"></select>
            <article class="profile-card">
              <div class="profile-head">
                <div id="profileTitle" class="profile-title"></div>
                <div class="badge">Selected</div>
              </div>
              <p id="profileDesc" class="desc"></p>
              <div class="meta-grid">
                <div class="meta"><small>Standard</small><strong id="profileStandard"></strong></div>
                <div class="meta"><small>Region</small><strong id="profileRegion"></strong></div>
                <div class="meta"><small>Paper Type</small><strong id="profilePaperType"></strong></div>
                <div class="meta"><small>TAC</small><strong id="profileTac"></strong></div>
                <div class="meta"><small>Paper Class</small><strong id="profilePaperClass"></strong></div>
              </div>
              <div id="profileWarning" class="profile-warning"></div>
            </article>
          </div>
          <div id="customPanel" class="hidden">
            <section id="iccDropzone" class="dropzone compact" tabindex="0" role="button">
              <div>
                <div class="plus">+</div>
                <div class="primary-text">Choose ICC File</div>
                <div class="secondary-text">Supports .icc and .icm format profiles</div>
              </div>
            </section>
            <input id="iccInput" type="file" accept=".icc,.icm">
            <div id="iccStatus" class="status">No custom ICC selected.</div>
            <div class="profile-warning">Please ensure your custom ICC profile is a valid CMYK color space profile.</div>
          </div>
        </section>

        <section id="result" class="result">
          <div class="summary">
            <div><strong id="total">0</strong><span>Total</span></div>
            <div><strong id="converted">0</strong><span>Converted</span></div>
            <div><strong id="skipped">0</strong><span>Skipped</span></div>
            <div><strong id="failed">0</strong><span>Failed</span></div>
            <div><strong id="risk">0</strong><span>High Risk</span></div>
          </div>
          <div id="notice" class="notice"></div>
        </section>
      </div>

      <aside class="card side-card">
        <section class="section">
          <h2>Source RGB Profile</h2>
          <div class="tabs">
            <button id="sourcePresetTab" class="tab active" type="button">Preset sRGB</button>
            <button id="sourceCustomTab" class="tab" type="button">Custom sRGB</button>
          </div>
          <div id="sourcePresetPanel">
            <select id="sourceProfileSelect"></select>
            <div id="sourceProfileNote" class="field-note"></div>
          </div>
          <div id="sourceCustomPanel" class="hidden">
            <section id="sourceIccDropzone" class="dropzone compact" tabindex="0" role="button">
              <div>
                <div class="plus">+</div>
                <div class="primary-text">Choose Source RGB ICC</div>
                <div class="secondary-text">Supports .icc and .icm source RGB profiles</div>
              </div>
            </section>
            <input id="sourceIccInput" type="file" accept=".icc,.icm">
            <div id="sourceIccStatus" class="status">No custom source RGB ICC selected.</div>
          </div>
        </section>

        <section class="section">
          <label class="label" for="renderingIntentSelect">Rendering Intent</label>
          <select id="renderingIntentSelect"></select>
          <div id="renderingIntentNote" class="field-note"></div>
          <label class="checkbox-row">
            <input id="ditheringInput" type="checkbox">
            <span>Enable Dithering</span>
          </label>
          <div class="field-note">Recommended for photographic images to reduce banding.</div>
        </section>

        <section class="section">
          <h2>Output Settings</h2>
          <label class="label" for="outputFormatSelect">Output Format</label>
          <select id="outputFormatSelect"></select>
          <div id="outputFormatNote" class="field-note"></div>

          <label class="label" style="margin-top: 18px;">Quality Upscale</label>
          <div class="factor-options" role="radiogroup" aria-label="Quality upscale">
            <button class="factor-option active" type="button" data-upscale-factor="1" role="radio" aria-checked="true">1x</button>
            <button class="factor-option" type="button" data-upscale-factor="2" role="radio" aria-checked="false">2x</button>
            <button class="factor-option" type="button" data-upscale-factor="4" role="radio" aria-checked="false">4x</button>
          </div>
          <div id="upscaleFactorNote" class="field-note">1x keeps the original pixel dimensions. 2x and 4x enlarge the output image.</div>
          <div class="actions">
            <div id="status" class="status">Please select images to convert.</div>
            <button id="generateBtn" class="button" type="button" disabled>Convert RGB to CMYK</button>
          </div>
        </section>

      </aside>
    </div>
  </main>
  <script>
    const presets = __PRESETS__;
    const defaultProfileId = "__DEFAULT_PROFILE_ID__";
    const sourceProfiles = __SOURCE_RGB_PRESETS__;
    const renderingIntents = __RENDERING_INTENTS__;
    const outputFormats = __OUTPUT_FORMATS__;
    const defaultSourceProfileId = "__DEFAULT_SOURCE_RGB_ID__";
    const defaultRenderingIntent = "__DEFAULT_RENDERING_INTENT__";
    const defaultOutputFormat = "__DEFAULT_OUTPUT_FORMAT__";
    const defaultDithering = __DEFAULT_DITHERING__;
    const presetTab = document.getElementById('presetTab');
    const customTab = document.getElementById('customTab');
    const presetPanel = document.getElementById('presetPanel');
    const customPanel = document.getElementById('customPanel');
    const profileSelect = document.getElementById('profileSelect');
    const iccDropzone = document.getElementById('iccDropzone');
    const iccInput = document.getElementById('iccInput');
    const iccStatus = document.getElementById('iccStatus');
    const sourcePresetTab = document.getElementById('sourcePresetTab');
    const sourceCustomTab = document.getElementById('sourceCustomTab');
    const sourcePresetPanel = document.getElementById('sourcePresetPanel');
    const sourceCustomPanel = document.getElementById('sourceCustomPanel');
    const sourceProfileSelect = document.getElementById('sourceProfileSelect');
    const sourceProfileNote = document.getElementById('sourceProfileNote');
    const sourceIccDropzone = document.getElementById('sourceIccDropzone');
    const sourceIccInput = document.getElementById('sourceIccInput');
    const sourceIccStatus = document.getElementById('sourceIccStatus');
    const renderingIntentSelect = document.getElementById('renderingIntentSelect');
    const renderingIntentNote = document.getElementById('renderingIntentNote');
    const outputFormatSelect = document.getElementById('outputFormatSelect');
    const outputFormatNote = document.getElementById('outputFormatNote');
    const upscaleFactorButtons = Array.from(document.querySelectorAll('[data-upscale-factor]'));
    const upscaleFactorNote = document.getElementById('upscaleFactorNote');
    let upscaleFactor = '1';
    const ditheringInput = document.getElementById('ditheringInput');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const generateBtn = document.getElementById('generateBtn');
    const statusEl = document.getElementById('status');
    const resultEl = document.getElementById('result');
    const files = [];
    let customIccFile = null;
    let customSourceIccFile = null;
    let profileMode = 'preset';
    let sourceProfileMode = 'preset';
    const allowed = new Set(['jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp']);

    function englishLabel(value) {
      return String(value || '').split('|')[0].trim();
    }

    function groupedPresets() {
      return presets.reduce((groups, profile) => {
        if (!groups[profile.group]) groups[profile.group] = [];
        groups[profile.group].push(profile);
        return groups;
      }, {});
    }

    function renderProfileSelect() {
      const groups = groupedPresets();
      profileSelect.innerHTML = '';
      Object.keys(groups).forEach(group => {
        const optgroup = document.createElement('optgroup');
        optgroup.label = group;
        groups[group].forEach(profile => {
          const option = document.createElement('option');
          option.value = profile.id;
          option.textContent = englishLabel(profile.display);
          optgroup.appendChild(option);
        });
        profileSelect.appendChild(optgroup);
      });
      profileSelect.value = defaultProfileId;
      renderProfileCard();
    }

    function selectedPreset() {
      return presets.find(profile => profile.id === profileSelect.value) || presets[0];
    }

    function renderProfileCard() {
      const profile = selectedPreset();
      document.getElementById('profileTitle').textContent = englishLabel(profile.display);
      document.getElementById('profileDesc').textContent = profile.description;
      document.getElementById('profileStandard').textContent = profile.standard;
      document.getElementById('profileRegion').textContent = profile.region;
      document.getElementById('profilePaperType').textContent = profile.paper_type;
      document.getElementById('profileTac').textContent = profile.tac;
      document.getElementById('profilePaperClass').textContent = profile.paper_class;
      document.getElementById('profileWarning').textContent = profile.available
        ? `ICC file ready: ${profile.filename}`
        : `Preset metadata is ready, but ${profile.filename} is not in profiles/presets. Generic CMYK conversion will be used.`;
      document.getElementById('profileWarning').className = profile.available ? 'profile-warning ok' : 'profile-warning';
    }

    function setMode(mode) {
      profileMode = mode;
      presetTab.classList.toggle('active', mode === 'preset');
      customTab.classList.toggle('active', mode === 'custom');
      presetPanel.classList.toggle('hidden', mode !== 'preset');
      customPanel.classList.toggle('hidden', mode !== 'custom');
    }

    function renderSourceControls() {
      sourceProfileSelect.innerHTML = '';
      sourceProfiles.forEach(profile => {
        const option = document.createElement('option');
        option.value = profile.id;
        option.textContent = englishLabel(profile.name);
        sourceProfileSelect.appendChild(option);
      });
      sourceProfileSelect.value = defaultSourceProfileId;

      renderingIntentSelect.innerHTML = '';
      renderingIntents.forEach(intent => {
        const option = document.createElement('option');
        option.value = intent.id;
        option.textContent = englishLabel(intent.label);
        renderingIntentSelect.appendChild(option);
      });
      renderingIntentSelect.value = defaultRenderingIntent;

      outputFormatSelect.innerHTML = '';
      outputFormats.forEach(format => {
        const option = document.createElement('option');
        option.value = format.id;
        option.textContent = format.label;
        outputFormatSelect.appendChild(option);
      });
      outputFormatSelect.value = defaultOutputFormat;
      setUpscaleFactor('1');
      ditheringInput.checked = Boolean(defaultDithering);
      renderSourceNotes();
    }

    function renderSourceNotes() {
      const profile = sourceProfiles.find(item => item.id === sourceProfileSelect.value) || sourceProfiles[0];
      const intent = renderingIntents.find(item => item.id === renderingIntentSelect.value) || renderingIntents[0];
      const format = outputFormats.find(item => item.id === outputFormatSelect.value) || outputFormats[0];
      const upscaleValue = Number(upscaleFactor || '1');
      sourceProfileNote.textContent = profile.available
        ? `${profile.description} ICC file ready: ${profile.filename}`
        : `${profile.description} ICC file is not bundled; use Custom sRGB to upload it.`;
      renderingIntentNote.textContent = intent.description;
      outputFormatNote.textContent = format.description;
      upscaleFactorNote.textContent = upscaleValue === 1
        ? '1x keeps the original pixel dimensions.'
        : `${upscaleValue}x enlarges output pixel dimensions using high-quality resampling.`;
    }

    function setUpscaleFactor(value) {
      upscaleFactor = ['1', '2', '4'].includes(String(value)) ? String(value) : '1';
      upscaleFactorButtons.forEach(button => {
        const isActive = button.dataset.upscaleFactor === upscaleFactor;
        button.classList.toggle('active', isActive);
        button.setAttribute('aria-checked', isActive ? 'true' : 'false');
      });
      renderSourceNotes();
    }

    function setSourceMode(mode) {
      sourceProfileMode = mode;
      sourcePresetTab.classList.toggle('active', mode === 'preset');
      sourceCustomTab.classList.toggle('active', mode === 'custom');
      sourcePresetPanel.classList.toggle('hidden', mode !== 'preset');
      sourceCustomPanel.classList.toggle('hidden', mode !== 'custom');
    }

    function fileKey(file) {
      return `${file.name}_${file.size}_${file.lastModified}`;
    }

    function addFiles(list) {
      const known = new Set(files.map(fileKey));
      Array.from(list).forEach(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!allowed.has(ext)) return;
        const key = fileKey(file);
        if (!known.has(key)) {
          files.push(file);
          known.add(key);
        }
      });
      renderFiles();
    }

    function renderFiles() {
      fileList.innerHTML = '';
      files.forEach(file => {
        const li = document.createElement('li');
        const size = file.size >= 1024 * 1024
          ? `${(file.size / 1024 / 1024).toFixed(1)} MB`
          : `${Math.max(1, Math.round(file.size / 1024))} KB`;
        li.innerHTML = `<span>${file.name}</span><span>${size}</span>`;
        fileList.appendChild(li);
      });
      generateBtn.disabled = files.length === 0;
      statusEl.textContent = files.length ? `Selected ${files.length} image(s).` : 'Please select images to convert.';
    }

    function wireDrop(target, input, callback) {
      target.addEventListener('click', () => input.click());
      target.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') input.click();
      });
      ['dragenter', 'dragover'].forEach(name => {
        target.addEventListener(name, event => {
          event.preventDefault();
          target.classList.add('dragover');
        });
      });
      ['dragleave', 'drop'].forEach(name => {
        target.addEventListener(name, event => {
          event.preventDefault();
          target.classList.remove('dragover');
        });
      });
      target.addEventListener('drop', event => callback(event.dataTransfer.files));
    }

    presetTab.addEventListener('click', () => setMode('preset'));
    customTab.addEventListener('click', () => setMode('custom'));
    profileSelect.addEventListener('change', renderProfileCard);
    sourcePresetTab.addEventListener('click', () => setSourceMode('preset'));
    sourceCustomTab.addEventListener('click', () => setSourceMode('custom'));
    sourceProfileSelect.addEventListener('change', renderSourceNotes);
    renderingIntentSelect.addEventListener('change', renderSourceNotes);
    outputFormatSelect.addEventListener('change', renderSourceNotes);
    upscaleFactorButtons.forEach(button => {
      button.addEventListener('click', () => setUpscaleFactor(button.dataset.upscaleFactor));
    });
    fileInput.addEventListener('change', event => addFiles(event.target.files));
    iccInput.addEventListener('change', event => {
      customIccFile = event.target.files[0] || null;
      iccStatus.textContent = customIccFile ? `Selected: ${customIccFile.name}` : 'No custom ICC selected.';
    });
    sourceIccInput.addEventListener('change', event => {
      customSourceIccFile = event.target.files[0] || null;
      sourceIccStatus.textContent = customSourceIccFile ? `Selected: ${customSourceIccFile.name}` : 'No custom source RGB ICC selected.';
    });
    wireDrop(dropzone, fileInput, addFiles);
    wireDrop(iccDropzone, iccInput, list => {
      customIccFile = Array.from(list).find(file => /\.(icc|icm)$/i.test(file.name)) || null;
      iccStatus.textContent = customIccFile ? `Selected: ${customIccFile.name}` : 'No valid ICC file selected.';
    });
    wireDrop(sourceIccDropzone, sourceIccInput, list => {
      customSourceIccFile = Array.from(list).find(file => /\.(icc|icm)$/i.test(file.name)) || null;
      sourceIccStatus.textContent = customSourceIccFile ? `Selected: ${customSourceIccFile.name}` : 'No valid source RGB ICC selected.';
    });

    generateBtn.addEventListener('click', async () => {
      if (!files.length) return;
      const form = new FormData();
      form.append('profile_mode', profileMode);
      form.append('profile_id', profileSelect.value);
      form.append('source_profile_mode', sourceProfileMode);
      form.append('source_profile_id', sourceProfileSelect.value);
      form.append('rendering_intent', renderingIntentSelect.value);
      form.append('enable_dithering', ditheringInput.checked ? '1' : '0');
      form.append('output_format', outputFormatSelect.value);
      form.append('upscale_factor', upscaleFactor);
      if (profileMode === 'custom' && customIccFile) form.append('custom_icc', customIccFile, customIccFile.name);
      if (sourceProfileMode === 'custom' && customSourceIccFile) form.append('custom_source_icc', customSourceIccFile, customSourceIccFile.name);
      files.forEach(file => form.append('images', file, file.name));
      generateBtn.disabled = true;
      statusEl.textContent = 'Uploading and converting, please wait...';
      resultEl.classList.remove('visible');

      try {
        const response = await fetch('/api/convert', { method: 'POST', body: form });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || 'Conversion failed');

        document.getElementById('total').textContent = data.stats.total;
        document.getElementById('converted').textContent = data.stats.converted;
        document.getElementById('skipped').textContent = data.stats.skipped;
        document.getElementById('failed').textContent = data.stats.failed;
        document.getElementById('risk').textContent = data.stats.high_risk;
        document.getElementById('notice').textContent = `${data.stats.icc_message}. CMYK_Output folder opened automatically.`;
        resultEl.classList.add('visible');
        statusEl.textContent = 'Finished.';
      } catch (error) {
        statusEl.innerHTML = `<span class="error">${error.message}</span>`;
      } finally {
        generateBtn.disabled = files.length === 0;
      }
    });

    renderProfileSelect();
    renderSourceControls();
    setMode('preset');
    setSourceMode('preset');
  </script>
</body>
</html>
"""


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip()
    return name or "upload_file"


def parse_multipart(headers, body: bytes) -> tuple[dict[str, str], list[tuple[str, str, bytes]]]:
    content_type = headers.get("Content-Type", "")
    parser_input = b"Content-Type: " + content_type.encode("utf-8") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
    message = BytesParser(policy=default).parsebytes(parser_input)
    fields: dict[str, str] = {}
    files: list[tuple[str, str, bytes]] = []

    if not message.is_multipart():
        return fields, files

    for part in message.iter_parts():
        field_name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if not field_name:
            continue
        if filename:
            files.append((field_name, safe_filename(filename), payload))
        else:
            fields[field_name] = payload.decode(part.get_content_charset() or "utf-8", errors="replace")

    return fields, files


def preset_payload() -> str:
    ensure_profile_dirs()
    payload = []
    for profile in PRESET_PROFILES:
        item = dict(profile)
        item["available"] = resolve_preset_path(profile["id"]) is not None
        payload.append(item)
    return json.dumps(payload, ensure_ascii=False)


def source_rgb_payload() -> str:
    ensure_source_profile_dirs()
    payload = []
    for profile in SOURCE_RGB_PROFILES:
        item = dict(profile)
        filename = item.get("filename")
        item["available"] = bool(filename and (SOURCE_RGB_PRESET_DIR / str(filename)).exists())
        payload.append(item)
    return json.dumps(payload, ensure_ascii=False)


def build_index() -> bytes:
    html = INDEX_HTML.replace("__PRESETS__", preset_payload())
    html = html.replace("__DEFAULT_PROFILE_ID__", DEFAULT_PROFILE_ID)
    html = html.replace("__SOURCE_RGB_PRESETS__", source_rgb_payload())
    html = html.replace("__RENDERING_INTENTS__", json.dumps(RENDERING_INTENTS, ensure_ascii=False))
    html = html.replace("__OUTPUT_FORMATS__", json.dumps(OUTPUT_FORMATS, ensure_ascii=False))
    html = html.replace("__DEFAULT_SOURCE_RGB_ID__", DEFAULT_SOURCE_RGB_ID)
    html = html.replace("__DEFAULT_RENDERING_INTENT__", DEFAULT_RENDERING_INTENT)
    html = html.replace("__DEFAULT_OUTPUT_FORMAT__", DEFAULT_OUTPUT_FORMAT)
    html = html.replace("__DEFAULT_DITHERING__", "true" if DEFAULT_DITHERING else "false")
    return html.encode("utf-8")


def resolve_selected_profile(fields: dict[str, str], files: list[tuple[str, str, bytes]]) -> tuple[Path | None, str]:
    ensure_profile_dirs()
    mode = fields.get("profile_mode", "preset")

    if mode == "custom":
        for field_name, filename, payload in files:
            if field_name != "custom_icc":
                continue
            ext = Path(filename).suffix.lower()
            if ext not in {".icc", ".icm"}:
                continue
            target = unique_path(CUSTOM_PROFILE_DIR / filename)
            target.write_bytes(payload)
            return target, f"Custom ICC: {filename}"
        return None, "Custom ICC not selected"

    profile_id = fields.get("profile_id", DEFAULT_PROFILE_ID)
    preset_path = resolve_preset_path(profile_id)
    profile = next((item for item in PRESET_PROFILES if item["id"] == profile_id), None)
    label = profile["name"] if profile else profile_id
    return preset_path, label


def resolve_source_rgb_profile(fields: dict[str, str], files: list[tuple[str, str, bytes]]) -> tuple[Path | None, str]:
    ensure_source_profile_dirs()
    mode = fields.get("source_profile_mode", "preset")

    if mode == "custom":
        for field_name, filename, payload in files:
            if field_name != "custom_source_icc":
                continue
            ext = Path(filename).suffix.lower()
            if ext not in {".icc", ".icm"}:
                continue
            target = unique_path(SOURCE_RGB_CUSTOM_DIR / filename)
            target.write_bytes(payload)
            return target, f"Custom source RGB: {filename}"
        return None, "Custom source RGB not selected"

    profile_id = fields.get("source_profile_id", DEFAULT_SOURCE_RGB_ID)
    source_path = resolve_source_profile_path(profile_id)
    profile = next((item for item in SOURCE_RGB_PROFILES if item["id"] == profile_id), None)
    label = str(profile["name"]) if profile else profile_id
    return source_path, label


def open_output_folder() -> None:
    try:
        os.startfile(str(OUTPUT_DIR))
    except Exception:
        pass


class AppHandler(BaseHTTPRequestHandler):
    server_version = "RGBToCMYKWeb/2.0"

    def log_message(self, format, *args):
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self.send_bytes(build_index(), "text/html; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/convert":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                self.send_json({"ok": False, "error": "\u6ca1\u6709\u6536\u5230\u6587\u4ef6\u3002"}, HTTPStatus.BAD_REQUEST)
                return
            if content_length > MAX_UPLOAD_BYTES:
                self.send_json({"ok": False, "error": "\u4e0a\u4f20\u6587\u4ef6\u8fc7\u5927\u3002"}, HTTPStatus.BAD_REQUEST)
                return

            body = self.rfile.read(content_length)
            fields, upload_parts = parse_multipart(self.headers, body)
            selected_profile_path, selected_profile_label = resolve_selected_profile(fields, upload_parts)
            source_profile_path, source_profile_label = resolve_source_rgb_profile(fields, upload_parts)
            rendering_intent = rendering_intent_value(fields.get("rendering_intent", DEFAULT_RENDERING_INTENT))
            enable_dithering = fields.get("enable_dithering", "1") == "1"
            output_format = output_format_by_id(fields.get("output_format", DEFAULT_OUTPUT_FORMAT))["id"]
            try:
                upscale_factor = int(fields.get("upscale_factor", "1"))
            except ValueError:
                upscale_factor = 1
            if upscale_factor not in {1, 2, 4}:
                upscale_factor = 1
            saved_paths: list[Path] = []

            ensure_directories()
            for field_name, filename, payload in upload_parts:
                if field_name != "images":
                    continue
                ext = Path(filename).suffix.lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue
                target = unique_path(INPUT_DIR / filename)
                target.write_bytes(payload)
                saved_paths.append(target)

            if not saved_paths:
                self.send_json({"ok": False, "error": "\u6ca1\u6709\u53ef\u5904\u7406\u7684\u56fe\u7247\u683c\u5f0f\u3002"}, HTTPStatus.BAD_REQUEST)
                return

            stats = run_conversion(
                saved_paths,
                selected_profile_path,
                selected_profile_label,
                source_profile_path,
                source_profile_label,
                rendering_intent,
                enable_dithering,
                output_format,
                upscale_factor,
            )
            if selected_profile_path is None:
                stats["icc_message"] = (
                    f"\u672a\u627e\u5230\u6240\u9009ICC\u6587\u4ef6: {selected_profile_label}\uff0c"
                    "\u672c\u6b21\u4f7f\u7528\u901a\u7528CMYK\u8f6c\u6362"
                )
            if source_profile_path is None:
                stats["icc_message"] += f" | Source RGB ICC not found: {source_profile_label}; built-in sRGB used"
            threading.Thread(target=open_output_folder, daemon=True).start()
            self.send_json(
                {
                    "ok": True,
                    "stats": {
                        "total": stats["total"],
                        "converted": stats["converted"],
                        "skipped": stats["skipped"],
                        "failed": stats["failed"],
                        "high_risk": stats["high_risk"],
                        "report_path": stats["report_path"],
                        "output_dir": stats["output_dir"],
                        "icc_message": stats["icc_message"],
                    },
                }
            )
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def send_bytes(self, content: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(content, "application/json; charset=utf-8", status)


def main() -> int:
    ensure_directories()
    ensure_profile_dirs()
    ensure_source_profile_dirs()
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    port = server.server_address[1]
    url = f"http://{HOST}:{port}/"
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    print(f"RGB to CMYK web tool is running: {url}")
    print("Close this window to stop the tool.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




