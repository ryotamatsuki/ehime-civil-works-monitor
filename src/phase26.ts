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
      heroLead.textContent = `国・愛媛県等の公式資料から、独立した公共土木事業として名称・事業主体・実施地域を確認できた県内${dataset.projects.length}事業を掲載しています。総事業費・工程・進捗・B/C・履歴は確認できた値だけを収録し、不明値は推測しません。`;
    }

    const notice = document.querySelector<HTMLElement>('.hero .notice');
    if (notice) {
      const strong = notice.querySelector('strong');
      const text = notice.querySelector('p');
      if (strong) strong.textContent = '掲載対象 · OFFICIAL-SOURCE PROJECT INVENTORY';
      if (text) text.textContent = '掲載案件は愛媛県が公式に選定した「重点事業」一覧ではなく、本サイトが複数の公式資料を横断して事業単位を整理したものです。県内の公共土木事業すべてを網羅するものではありません。';
    }

    const firstMetricLabel = document.querySelector<HTMLElement>('.dashboard .metric span');
    if (firstMetricLabel) {
      firstMetricLabel.innerHTML = 'PROJECTS<br>公式資料確認事業';
    }

    if (!document.querySelector('.phase26-summary')) {
      const section = document.createElement('section');
      section.className = 'phase26-summary';
      section.id = 'publishing-criteria';
      section.innerHTML = `
        <div>
          <p class="eyebrow">掲載対象 · PUBLICATION CRITERIA</p>
          <h2>公式資料から確認した公共土木事業 ${dataset.projects.length}件</h2>
        </div>
        <div class="phase26-metrics">
          <span><strong>${dataset.projects.length}</strong>掲載事業</span>
          <span><strong>+59</strong>Phase 2.6追加</span>
          <span><strong>66</strong>道路</span>
          <span><strong>22</strong>砂防</span>
        </div>
        <p class="phase26-definition">本サイトでは、愛媛県内で実施中または具体的に計画されている公共土木事業のうち、国・愛媛県等の公式資料から<strong>独立した事業として名称・事業主体・実施地域を確認できるもの</strong>を掲載対象としています。掲載件数は、県が公式に選定した重点事業数でも、県内の全公共土木事業数でもありません。</p>
        <details class="phase26-policy">
          <summary>掲載基準・データについて詳しく見る</summary>
          <div class="phase26-policy-body">
            <section>
              <h3>掲載する事業</h3>
              <p>道路、河川、砂防、港湾、海岸、都市、ダム等について、公式資料上で政策・予算・事業評価等の単位として独立したProjectであることを確認できる事業を収録します。県施行に加え、愛媛県内で実施される国直轄等の事業も、事業主体を明示したうえで対象とします。</p>
            </section>
            <section>
              <h3>掲載の最低条件</h3>
              <ol>
                <li>公式一次資料で独立した事業名を確認できること</li>
                <li>事業主体または所管を確認できること</li>
                <li>実施市町・地域を合理的に特定できること</li>
                <li>既存掲載事業との重複や、上位Projectに属する工区・工事でないことを確認できること</li>
              </ol>
              <p>総事業費、完成年度、進捗率、B/C、年度予算等は掲載の必須条件ではありません。確認できない数値は0として扱わず、未確認のまま明示します。</p>
            </section>
            <section>
              <h3>主な確認資料</h3>
              <p>「えひめの土木」、道路の整備に関するプログラム、公共事業評価資料、当初・補正予算資料、地方局・土木事務所の事業紹介、国土交通省・四国地方整備局資料、発注見通し等を横断して候補を確認しています。</p>
            </section>
            <section>
              <h3>原則として掲載しないもの</h3>
              <p>単一の工事契約、測量・設計等の委託業務、独立事業であることを確認できない単なる施設名・路線名・河川名、民間事業、市町単独事業は原則としてcanonical Projectにはしません。発注見通しは候補探索に利用しますが、契約1件をそのまま1事業として数えません。</p>
            </section>
            <section>
              <h3>網羅性と位置情報</h3>
              <p>公式資料から事業単位を確認できた案件を順次追加しているため、県内の公共土木事業すべてを網羅しているとは限りません。また、公式GIS形状が確認できない案件は検索・俯瞰用の代表点を表示しており、正確な施工区域や道路線形を示すものではありません。</p>
            </section>
          </div>
        </details>`;
      document.querySelector('#dashboard-root')?.insertAdjacentElement('afterend', section);
    }
  } catch {
    // Core rendering remains usable if this optional explanatory layer fails.
  }
}

void phase26();
