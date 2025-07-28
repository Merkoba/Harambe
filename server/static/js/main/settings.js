App.show_settings = () => {
  let created = App.msg_settings !== undefined

  if (!created) {
    App.make_msg(`settings`, `Settings`)
  }

  App.msg_settings.show()

  if (!created) {
    let select = DOM.el(`#settings_theme`)

    for (let [i, theme] of App.themes.entries()) {
      let option = DOM.create(`option`)
      option.value = theme[0]
      option.textContent = theme[1]
      select.appendChild(option)

      let desc = DOM.create(`option`, `info_option`)
      desc.value = ``
      desc.textContent = theme[2]
      desc.disabled = true
      select.appendChild(desc)

      if (i < App.themes.length - 1) {
        let hr = DOM.create(`hr`)
        select.append(hr)
      }
    }

    select.value = App.get_cookie(`theme`) || App.theme

    DOM.ev(select, `change`, () => {
      App.set_cookie(`theme`, select.value)
    })

    App.cycle_select(`theme`)

    let font_size = DOM.el(`#settings_font_size`)
    font_size.value = App.get_cookie(`font_size`) || App.font_size

    DOM.ev(font_size, `blur`, () => {
      App.set_cookie(`font_size`, font_size.value)
    })

    let fs_cycles = [
      `14`,
      `15`,
      `16`,
      `17`,
      `18`,
      `19`,
      `20`,
      `21`,
      `22`,
      `23`,
      `24`,
    ]

    App.register_cycle(fs_cycles, `font_size`)

    let font_family = DOM.el(`#settings_font_family`)
    font_family.value = App.get_cookie(`font_family`) || App.font_family

    DOM.ev(font_family, `blur`, () => {
      App.set_cookie(`font_family`, font_family.value)
    })

    let ff_cycles = [
      `serif`,
      `sans-serif`,
      `monospace`,
      `cursive`,
      `fantasy`,
    ]

    App.register_cycle(ff_cycles, `font_family`)

    DOM.ev(`#settings_reset`, `click`, () => {
      if (confirm(`Are you sure you want to reset the settings?`)) {
        App.clear_cookie(`theme`)
        App.clear_cookie(`font_size`)
        App.clear_cookie(`font_family`)
        App.reload()
      }
    })

    DOM.ev(`#settings_apply`, `click`, () => {
      App.reload()
    })
  }
}

App.register_cycle = (cycles, name) => {
  let prev = DOM.el(`#settings_${name}_prev`)
  let next = DOM.el(`#settings_${name}_next`)
  let el = DOM.el(`#settings_${name}`)
  let item = el.closest(`.settings_item`)

  function action(dir) {
    let current = el.value
    let index = cycles.indexOf(current)

    if (dir === `next`) {
      index += 1
    }
    else if (dir === `prev`) {
      index -= 1
    }

    if ((index < 0) || (index >= cycles.length)) {
      return
    }

    el.value = cycles[index]
    App.set_cookie(name, el.value)
  }

  DOM.ev(prev, `click`, () => {
    action(`prev`)
  })

  DOM.ev(next, `click`, () => {
    action(`next`)
  })

  DOM.ev(item, `wheel`, (e) => {
    action(e.deltaY < 0 ? `next` : `prev`)
    e.preventDefault()
  })
}

App.cycle_select = (name) => {
  let select = DOM.el(`#settings_${name}`)

  DOM.ev(select, `wheel`, (e) => {
    let cycles = Array.from(select.options)
    .filter(o => !o.disabled)
    .map(option => option.value)

    if (cycles.length < 2) {
      return
    }

    let current = select.value
    let index = cycles.indexOf(current)
    let dir = e.deltaY < 0 ? `prev` : `next`

    if (dir === `next`) {
      index += 1
    }
    else if (dir === `prev`) {
      index -= 1
    }

    if (index < 0 || (index >= cycles.length)) {
      return
    }

    select.value = cycles[index]
    App.set_cookie(`theme`, select.value)
    e.preventDefault()
  })
}