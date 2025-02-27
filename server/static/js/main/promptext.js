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
    c.appendChild(input)

    let buttons = DOM.create(`div`)
    buttons.id = `prompt_buttons`
    c.appendChild(buttons)

    let submit_button = DOM.create(`div`, `prompt_button`)
    submit_button.id = `prompt_submit`
    submit_button.textContent = `Submit`
    buttons.appendChild(submit_button)

    for (let btn of args.buttons) {
      let el = DOM.create(`div`, `prompt_button prompt_button_2`)
      el.textContent = btn.text

      DOM.ev(el, `click`, () => {
        if (btn.callback(input.value)) {
          msg.close()
        }
      })

      buttons.appendChild(el)
    }

    msg.set(c)

    function update_submit_button() {
      if (args.max > 0) {
        submit_button.textContent = `Submit (${input.value.length}/${args.max})`
      }
      else {
        submit_button.textContent = `Submit (${input.value.length})`
      }
    }

    DOM.ev(input, `input`, (e) => {
      if (args.max > 0) {
        if (input.value.length > args.max) {
          input.value = input.value.substring(0, args.max).trim()
        }
      }

      update_submit_button()
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

    DOM.ev(submit_button, `click`, () => {
      this.submit()
    })

    update_submit_button()
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