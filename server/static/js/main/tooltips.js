class Tooltip {
  static delay = 500

  constructor(args = {}) {
    let def_args = {
      text: `Tooltip`,
      generate: () => {},
    }

    App.fill_def_args(def_args, args)
    this.args = args
    this.tip = null

    DOM.ev(args.element, `mouseover`, (e) => {
      if (this.tip) {
        return
      }

      Tooltip.debouncer.call(e, this)
    })

    DOM.ev(args.element, `mouseout`, () => {
      Tooltip.debouncer.cancel()

      if (this.tip) {
        this.tip.remove()
        this.tip = null
      }
    })
  }

  show(e) {
    let tip = DOM.create(`div`, `tooltip`)
    tip.textContent = this.args.generate()

    tip.style.position = `fixed`
    tip.style.top = `${e.clientY}px`
    tip.style.left = `${e.clientX + 10}px`
    tip.style.zIndex = 999
    tip.style.backgroundColor = `#333`
    tip.style.color = `#fff`
    tip.style.padding = `0.5rem`

    this.tip = tip
    document.body.appendChild(tip)

    let bbox = tip.getBoundingClientRect()
    let top = e.clientY

    if (bbox.bottom >= window.innerHeight) {
      top -= bbox.height
    }
  }
}

Tooltip.debouncer = App.create_debouncer((e, tip) => {
  tip.show(e)
}, Tooltip.delay)