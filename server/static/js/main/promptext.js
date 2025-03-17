class Promptext {
  static instance = null

  constructor(args = {}) {
    let def_args = {
      placeholder: `Enter Text`,
      max: 0,
      multi: false,
      value: ``,
      buttons: [],
      password: false,
    }

    App.fill_def_args(def_args, args)

    let msg = Msg.factory({
      persistent: false,
      disable_content_padding: true,
      clear_editables: true,
      clear_editables_full: true,
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
    input.spellcheck = true
    input.placeholder = args.placeholder
    input.value = args.value

    if (args.password) {
      input.type = `password`
    }

    c.appendChild(input)
    let buttons = DOM.create(`div`)
    buttons.id = `prompt_buttons`
    c.appendChild(buttons)

    for (let btn of args.buttons) {
      let el = DOM.create(`div`, `prompt_button prompt_button_2`)
      el.textContent = btn.text

      DOM.ev(el, `click`, () => {
        this.button_action(btn)
      })

      buttons.appendChild(el)
    }

    let button = DOM.create(`div`, `prompt_button`)
    button.id = `prompt_submit`
    button.textContent = `Submit`
    buttons.appendChild(button)

    msg.set(c)

    DOM.ev(input, `input`, (e) => {
      if (args.max > 0) {
        if (input.value.length > args.max) {
          input.value = input.value.substring(0, args.max).trim()
        }
      }

      this.update_button()
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
      else if (e.key === `Tab`) {
        e.preventDefault()
      }
    })

    DOM.ev(input, `keyup`, (e) => {
      if (e.key === `Tab`) {
        if (args.buttons.length > 0) {
          this.button_action(args.buttons[0])
        }

        e.preventDefault()
      }
    })

    DOM.ev(button, `click`, () => {
      this.submit()
    })

    this.button = button
    this.input = input
    this.args = args
    this.msg = msg
    Promptext.instance = this
    this.update_button()
    msg.show()
    input.focus()
  }

  async submit() {
    let ans = await this.args.callback(this.input.value)

    if (!ans) {
      this.msg.close()
    }
  }

  insert(text) {
    let value = this.input.value.trim()
    this.input.value = `${value} ${text.trim()} `
    this.update_button()
    this.input.selectionStart = this.input.value.length
    this.input.focus()
  }

  button_action(btn) {
    if (btn.callback(this.input.value)) {
      this.msg.close()
    }
  }

  focus() {
    this.input.focus()
  }

  update_button() {
    if (this.args.max > 0) {
      this.button.textContent = `Submit (${this.input.value.length}/${this.args.max})`
    }
    else {
      this.button.textContent = `Submit (${this.input.value.length})`
    }
  }
}