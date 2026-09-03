import './phase26.css';
import type { ProjectCollection } from './types';

const base = import.meta.env.BASE_URL;

async function waitForHome() {
  for (let frame = 0; frame < 180; frame += 1) {
    if (document.querySelector('.hero, .detail-main, .error-panel')) return;
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }
}

async function phase26() {
  try {
    const response = await fetch(`${base}data/projects.json`);
    if (!response.ok) return;
    const dataset = await response.json() as ProjectCollection;
    await waitForHome();
    if (document.querySelector('.detail-main')) return;

    const heroLead = document.querySelector<HTMLElement>('.hero .lead');
    if (heroLead) {
      heroLead.textContent = `県内${dataset.projects.length}事業を地図で俯瞰し、一次資料で確認できた総事業費・工程・進捗・B/C・履歴を同じ画面で追跡します。値が確認できない案件は推測せずInventoryとして明示します。`;
    }

    const notice = document.querySelector<HTMLElement>('.hero .notice');
    if (notice) {
      const strong = notice.querySelector('strong');
      const text = notice.querySelector('p');
      if (strong) strong.textContent = 'PHASE 2.6 · COMPREHENSIVE INVENTORY / 2026-09-03';
      if (text) text.textContent = '公式資料を横断して事業母集団を再構築。単一工事・業務・施設名をProjectとして水増しせず、独立した事業として確認できる案件を追加しています。';
    }

    if (!document.querySelector('.phase26-summary')) {
      const section = document.createElement('section');
      section.className = 'phase26-summary';
      section.innerHTML = `
        <div><p class="eyebrow">PHASE 2.6 · POPULATION REBUILD</p><h2>50件の代表サンプルから、109件のcanonical inventoryへ。</h2></div>
        <div class="phase26-metrics">
          <span><strong>${dataset.projects.length}</strong>CANONICAL</span>
          <span><strong>+59</strong>NEW PROJECTS</span>
          <span><strong>66</strong>ROAD</span>
          <span><strong>22</strong>SABO</span>
        </div>
        <p>道路整備プログラムと公共事業評価の個別事業を中心に母集団を拡張。予算額・総事業費・進捗が未確認でも、事業identity・operator・市町・一次資料が確認できればInventoryとして収録します。</p>`;
      document.querySelector('#dashboard-root')?.insertAdjacentElement('afterend', section);
    }
  } catch {
    // Core rendering remains usable if this optional explanatory layer fails.
  }
}

void phase26();
