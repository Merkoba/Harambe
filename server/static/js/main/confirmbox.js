class Confirmbox {
  static instance = null

  constructor(args = {}) {
    if (Confirmbox.instance) {
      Confirmbox.instance.msg.close()
    }

    let def_args = {
      message: `Are you sure ?`,
      yes: `Yes`,
      no: `No`,
      question: true,
    }

    App.fill_def_args(def_args, args)

    let msg = Msg.factory({
      persistent: false,
      after_close: () => {
        Confirmbox.instance = null
      },
    })

    let c = DOM.create(`div`)
    c.id = `confirmbox_container`
    let m = DOM.create(`div`)
    m.id = `confirmbox_message`
    m.innerHTML = args.message

    if (args.question) {
      m.innerHTML += `&nbsp;?`
    }

    let btns = DOM.create(`div`, `dialog_container`)
    btns.id = `confirmbox_buttons`
    let n = DOM.create(`div`, `aero_button`, `confirmbox_opts_no`)
    n.textContent = args.no
    let y = DOM.create(`div`, `aero_button`, `confirmbox_opts_yes`)
    y.textContent = args.yes

    c.appendChild(m)
    btns.appendChild(n)
    btns.appendChild(y)
    c.appendChild(btns)

    msg.set(c)
    App.msg_confirmbox = msg

    App.bind_button(`confirmbox_opts_no`, () => {
      if (args.callback_no) {
        args.callback_no()
      }
    })

    App.bind_button(`confirmbox_opts_yes`, () => {
      this.action()
    })

    this.args = args
    this.msg = msg
    Confirmbox.instance = this
    msg.show()
  }

  action() {
    if (this.args.callback_yes) {
      this.args.callback_yes()
    }

    this.msg.close()
  }
}