class Popmsg {
  static instance = null

  constructor(message, callback, html = false) {
    let msg = Msg.factory({
      persistent: false,
      after_close: callback,
    })

    this.msg = msg
    this.date = Date.now()
    Popmsg.instance = this
    let content = DOM.create(`div`, `popmsg_content`)

    if (html) {
      content.innerHTML = message
    }
    else {
      content.textContent = message
    }

    content.tabIndex = 0

    msg.set(content)
    msg.show()

    DOM.el(`.popmsg_content`, message.content).focus()
  }
}