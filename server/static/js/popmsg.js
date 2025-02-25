class Popmsg {
  static instance = null

  constructor(message, callback) {
    let msg = Msg.factory({
      persistent: false,
      after_close: callback,
    })

    this.msg = msg
    Popmsg.instance = this
    msg.show(message)
  }
}