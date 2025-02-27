class Promptext {
  static instance = null

  constructor(args = {}) {
    let def_args = {
      placeholder: `Enter Text`,
      max: 0,
      multi: false,
      value: ``,
      buttons: [],
    }

    fill_def_args(def_args, args)

    let msg = Msg.factory({
      persistent: false,
      disable_content_padding: true,
    })

    let c = DOM.create(`div`)
    c.id = `prompt_container`
    let input

    if (args.multi) {
      input = DOM.create(`textarea`)
    }
    else {
      input = DOM.create(`input`)
    }

    input.rows = 5
    input.id = `prompt_input`
    input.type = `text`
    input.placeholder = args.placeholder
    input.value = args.value
    let btn = DOM.create(`div`)
    btn.id = `prompt_submit`
    btn.textContent = `Submit`
    c.appendChild(input)
    c.appendChild(btn)
    msg.set(c)

    function update_btn() {
      if (args.max > 0) {
        btn.textContent = `Submit (${input.value.length}/${args.max})`
      }
      else {
        btn.textContent = `Submit (${input.value.length})`
      }
    }

    DOM.ev(input, `input`, (e) => {
      if (args.max > 0) {
        if (input.value.length > args.max) {
          input.value = input.value.substring(0, args.max).trim()
        }
      }

      update_btn()
    })

    DOM.ev(input, `keydown`, (e) => {
      if (e.key === `Enter`) {
        if (args.multi) {
          if (e.shiftKey || e.ctrlKey) {
            this.submit()
            e.preventDefault()
          }
        }
        else {
          this.submit()
          e.preventDefault()
        }
      }
    })

    DOM.ev(btn, `click`, this.submit)
    update_btn()
    this.input = input
    this.args = args
    this.msg = msg
    Promptext.instance = this
    msg.show()
    input.focus()
  }

  async submit() {
    let ans = await this.args.callback(this.input.value)

    if (!ans) {
      this.msg.close()
    }
  }
}