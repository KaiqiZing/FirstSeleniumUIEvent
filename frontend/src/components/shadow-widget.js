// Shadow DOM 复现组件：原生 Web Component + attachShadow(open)
// shadow-inner-box：一层影子节点内的小卡片
// shadow-demo-box：外层影子内放置输入框，并内嵌 shadow-inner-box（二层影子）

const SHADOW_STYLE = `
  :host { display: block; }
  .scard { border: 1.5px solid #d8d4c8; border-radius: 10px; padding: 14px 16px; background: #fffdf8; }
  .srow { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .sbtn {
    border: 1px solid #2f6f5c; background: #2f6f5c; color: #fff;
    border-radius: 6px; padding: 7px 14px; font-size: 13px; cursor: pointer;
    font-family: inherit;
  }
  .sbtn:hover { background: #24584a; border-color: #24584a; }
  .sinp {
    padding: 7px 10px; border: 1.5px solid #d8d4c8; border-radius: 6px;
    outline: none; font-size: 13px; width: 180px; font-family: inherit;
  }
  .sinp:focus { border-color: #2f6f5c; }
  .sst { margin: 10px 0 0; color: #4a4844; font-size: 13px; }
`

class ShadowInnerBox extends HTMLElement {
  connectedCallback() {
    if (this._built) return
    this._built = true
    const root = this.attachShadow({ mode: 'open' })
    root.innerHTML = ''
    const style = document.createElement('style')
    style.textContent = SHADOW_STYLE
    root.appendChild(style)
    const card = document.createElement('div')
    card.className = 'scard'
    card.innerHTML = `
      <div class="srow">
        <span style="font-size:13px">内部子任务</span>
        <button class="sbtn" type="button">执行内部任务</button>
      </div>
      <p class="sst">内部状态：待执行</p>`
    root.appendChild(card)
    const btn = card.querySelector('button')
    const st = card.querySelector('.sst')
    btn.addEventListener('click', () => {
      st.textContent = '内部状态：已执行完成'
      this.dispatchEvent(
        new CustomEvent('shadow-inner-done', { bubbles: true, composed: true })
      )
    })
  }
}

class ShadowDemoBox extends HTMLElement {
  connectedCallback() {
    if (this._built) return
    this._built = true
    const root = this.attachShadow({ mode: 'open' })
    const style = document.createElement('style')
    style.textContent = SHADOW_STYLE
    root.appendChild(style)
    const card = document.createElement('div')
    card.className = 'scard'
    card.innerHTML = `
      <div class="srow">
        <span style="font-size:13px">汇总台账</span>
        <input class="sinp" type="text" placeholder="请输入台账内容" />
        <button class="sbtn" type="button">外层保存</button>
      </div>
      <p class="sst">外层状态：未保存</p>
      <div style="margin-top:12px">
        <shadow-inner-box></shadow-inner-box>
      </div>`
    root.appendChild(card)

    const input = card.querySelector('input')
    const save = card.querySelector('button')
    const st = card.querySelector('.sst')
    save.addEventListener('click', () => {
      st.textContent = `外层状态：已保存「${input.value || '（空）'}」`
      this.dispatchEvent(
        new CustomEvent('shadow-outer-done', {
          bubbles: true,
          composed: true,
          detail: { value: input.value }
        })
      )
    })
  }
}

if (!customElements.get('shadow-inner-box')) {
  customElements.define('shadow-inner-box', ShadowInnerBox)
}
if (!customElements.get('shadow-demo-box')) {
  customElements.define('shadow-demo-box', ShadowDemoBox)
}

export { ShadowDemoBox, ShadowInnerBox }
