DOM.ev(document, `keydown`, (e) => {
  let n = parseInt(e.key)

  if (e.key === `Enter`) {
    if (Popmsg.instance && Popmsg.instance.msg.is_open()) {
      let now = Date.now()

      if ((now - Popmsg.instance.date) > 100) {
        e.preventDefault()
        Popmsg.instance.msg.close()
      }
    }
    else if (Confirmbox.instance && Confirmbox.instance.msg.is_open()) {
      e.preventDefault()
      Confirmbox.instance.action()
    }
    else if (Msg.msg && Msg.msg.any_open()) {
      let content = Msg.msg.highest_instance().content
      let dialog = DOM.el(`.dialog_container`, content)

      if (dialog) {
        let first = DOM.el(`.aero_button`, dialog)

        if (first) {
          e.preventDefault()
          first.click()
        }
      }
    }
  }
  else if (!isNaN(n) && (n >= 1) && (n <= 9)) {
    if (Msg.msg && Msg.msg.any_open()) {
      let content = Msg.msg.highest_instance().content
      let dialog = DOM.el(`.dialog_container`, content)

      if (dialog) {
        let buttons = DOM.els(`.aero_button`, dialog)

        if (n <= buttons.length) {
          e.preventDefault()
          buttons[n - 1].click()
        }
      }
    }
    else if (vars && (vars.mode === `index`)) {
      let c = DOM.el(`#buttons`)
      let buttons = DOM.els(`button`, c)

      if (n <= buttons.length) {
        e.preventDefault()
        buttons[n - 1].click()
      }
    }
  }
})

function singplural(what, length) {
  if (length === 1) {
    return what
  }

  return `${what}s`
}

function shuffle_array(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]]
  }

  return array
}

async function copy_to_clipboard(text) {
  navigator.clipboard.writeText(text)
}

function select_all(el) {
  let selection = window.getSelection()
  let range = document.createRange()
  range.selectNodeContents(el)
  selection.removeAllRanges()
  selection.addRange(range)
}

function is_image(file) {
  return file.type.match(`image/*`)
}

function is_audio(file) {
  return file.type.match(`audio/*`)
}

function is_video(file) {
  return file.type.match(`video/*`)
}

function set_css_var(name, value) {
  document.documentElement.style.setProperty(`--${name}`, value)
}

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}

function contains_url(text) {
  return text.match(/(https?:\/\/|www\.)\S+/gi)
}

function prompt_text(args = {}) {
  a = new Promptext(args)
}

function popmsg(message, callback) {
  new Popmsg(message, callback)
}

function remove_multiple_empty_lines(s) {
  return s.replace(/\n\s*\n/g, `\n\n`)
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function setup_admin_opts(mode = `normal`) {
  vars.msg_admin_opts = Msg.factory()
  let template = DOM.el(`#template_admin_opts`)
  vars.msg_admin_opts.set(template.innerHTML)

  DOM.ev(`#admin_opts_posts`, `click`, (e) => {
    vars.msg_admin_opts.close()

    if (vars.mode.includes(`admin`) || (mode === `admin`)) {
      window.location = `/admin/posts`
    }
    else {
      window.location = `/list/posts`
    }
  })

  DOM.ev(`#admin_opts_reactions`, `click`, (e) => {
    vars.msg_admin_opts.close()

    if (vars.mode.includes(`admin`) || (mode === `admin`)) {
      window.location = `/admin/reactions`
    }
    else {
      window.location = `/list/reactions`
    }
  })

  if (DOM.el(`#admin_opts_users`)) {
    DOM.ev(`#admin_opts_users`, `click`, (e) => {
      vars.msg_admin_opts.close()
      window.location = `/admin/users`
    })
  }

  let ret = DOM.el(`#admin_opts_return`)

  if (ret) {
    DOM.ev(ret, `click`, (e) => {
      vars.msg_admin_opts.close()
      window.location = `/`
    })
  }
}

function setup_explore_opts() {
  vars.msg_explore_opts = Msg.factory()
  let template = DOM.el(`#template_explore_opts`)
  vars.msg_explore_opts.set(template.innerHTML)

  DOM.ev(`#explore_opts_fresh`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/fresh`
  })

  DOM.ev(`#explore_opts_posts`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/list/posts`
  })

  DOM.ev(`#explore_opts_reactions`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/list/reactions`
  })

  DOM.ev(`#explore_opts_random`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/random`
  })

  let ret = DOM.el(`#explore_opts_return`)

  if (ret) {
    DOM.ev(ret, `click`, (e) => {
      vars.msg_admin_opts.close()
      window.location = `/`
    })
  }
}

function setup_you_opts(username) {
  vars.msg_you_opts = Msg.factory()
  let template = DOM.el(`#template_you_opts`)
  vars.msg_you_opts.set(template.innerHTML)

  DOM.ev(`#you_opts_posts`, `click`, (e) => {
    vars.msg_you_opts.close()
    window.location = `/list/posts?username=${username}`
  })

  DOM.ev(`#you_opts_reactions`, `click`, (e) => {
    vars.msg_you_opts.close()
    window.location = `/list/reactions?username=${username}`
  })

  DOM.ev(`#you_opts_edit_name`, `click`, (e) => {
    vars.msg_you_opts.close()
    edit_name()
  })

  DOM.ev(`#you_opts_edit_password`, `click`, (e) => {
    vars.msg_you_opts.close()
    edit_password()
  })

  DOM.ev(`#you_opts_logout`, `click`, (e) => {
    let confirm_args = {
      message: `Are you sure you want to logout ?`,
      callback_yes: () => {
        window.location = `/logout`
      },
    }

    confirmbox(confirm_args)
  })

  let ret = DOM.el(`#you_opts_return`)

  if (ret) {
    DOM.ev(ret, `click`, (e) => {
      vars.msg_admin_opts.close()
      window.location = `/`
    })
  }
}

function setup_user_opts() {
  vars.msg_user_opts = Msg.factory()
  let template = DOM.el(`#template_user_opts`)
  vars.msg_user_opts.set(template.innerHTML)

  DOM.ev(`#user_opts_posts`, `click`, (e) => {
    vars.msg_user_opts.close()
    let user_id = vars.user_opts_user_id

    if (vars.mode.includes(`admin`)) {
      window.location = `/admin/posts?user_id=${user_id}`
    }
    else {
      window.location = `/list/posts?user_id=${user_id}`
    }
  })

  DOM.ev(`#user_opts_reactions`, `click`, (e) => {
    vars.msg_user_opts.close()
    let user_id = vars.user_opts_user_id

    if (vars.mode.includes(`admin`)) {
      window.location = `/admin/reactions?user_id=${user_id}`
    }
    else {
      window.location = `/list/reactions?user_id=${user_id}`
    }
  })

  if (DOM.el(`#user_opts_user`)) {
    DOM.ev(`#user_opts_user`, `click`, (e) => {
      vars.msg_user_opts.close()
      let user_id = vars.user_opts_user_id
      window.location = `/edit_user/${user_id}`
    })
  }
}

function fill_def_args(def, args) {
  for (let key in def) {
    if ((args[key] === undefined) && (def[key] !== undefined)) {
      args[key] = def[key]
    }
  }
}

function confirmbox(args = {}) {
  new Confirmbox(args)
}

function edit_reaction_opts() {
  vars.msg_edit_reaction_opts = Msg.factory()
  let template = DOM.el(`#template_edit_reaction_opts`)
  vars.msg_edit_reaction_opts.set(template.innerHTML)

  DOM.ev(`#edit_reaction_opts_text`, `click`, (e) => {
    vars.msg_edit_reaction_opts.close()
    let id = parseInt(vars.active_item.dataset.id)
    react_text(id)
  })

  DOM.ev(`#edit_reaction_opts_icon`, `click`, (e) => {
    vars.msg_edit_reaction_opts.close()
    let id = parseInt(vars.active_item.dataset.id)
    react_icon(id)
  })
}

function setup_reaction_opts() {
  edit_reaction_opts()
  vars.msg_reaction_opts = Msg.factory()
  let template = DOM.el(`#template_reaction_opts`)
  vars.msg_reaction_opts.set(template.innerHTML)

  DOM.ev(`#reaction_opts_edit`, `click`, (e) => {
    vars.msg_reaction_opts.close()
    vars.msg_edit_reaction_opts.show()
  })

  DOM.ev(`#reaction_opts_delete`, `click`, (e) => {
    vars.msg_reaction_opts.close()
    delete_reaction(vars.active_item.dataset.id)
  })
}

function regex_u(c, n) {
  return `${c}{${n}}`
}

function regex_t(c, n) {
  let u = regex_u(c, n)
  return `(?:(?!${u}|\\s).)`
}

function regex_t2(c, n) {
  let u = regex_u(c, n)
  return `(?:(?!${u}).)`
}

function char_regex_1(char, n = 1) {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t = regex_t(c, n)
  let t2 = regex_t2(c, n)
  let regex = `${u}(${t}${t2}*${t}|${t})${u}`
  return new RegExp(regex, `g`)
}

function char_regex_2(char, n = 1) {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t = regex_t(c, n)
  let regex = `(?:^|\\s)${u}(${t}.*?${t}|${t})${u}(?:$|\\s)`
  return new RegExp(regex, `g`)
}

function char_regex_3(char, n = 1) {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t2 = regex_t2(c, n)
  let regex = `${u}(${t2}+)${u}`
  return new RegExp(regex, `g`)
}

to_bold = (text) => {
  return `<span class='md_highlight'>${text}</span>`
}

function parse_markdown(text) {
  function action(regex, func, full = false) {
    let matches = [...text.matchAll(regex)]

    for (let match of matches) {
      if (full) {
        text = text.replace(match[0], func(match[0]))
      }
      else {
        text = text.replace(match[0], func(match[1]))
      }
    }
  }

  action(char_regex_3(`\``), to_bold)
  action(char_regex_3(`"`), to_bold, true)
  action(char_regex_1(`*`, 2), to_bold)
  action(char_regex_1(`*`), to_bold)
  action(char_regex_2(`_`, 2), to_bold)
  action(char_regex_2(`_`), to_bold)
  return text
}

function escape_regex(s) {
  return s.replace(/[^A-Za-z0-9]/g, `\\$&`)
}

function create_debouncer(func, delay) {
  if (typeof func !== `function`) {
    print_error(`Invalid debouncer function`)
    return
  }

  if ((typeof delay !== `number`) || (delay < 1)) {
    print_error(`Invalid debouncer delay`)
    return
  }

  let timer
  let obj = {}

  function clear() {
    clearTimeout(timer)
    timer = undefined
  }

  function run(...args) {
    func(...args)
  }

  obj.call = (...args) => {
    clear()

    timer = setTimeout(() => {
      run(...args)
    }, delay)
  }

  obj.call_2 = (...args) => {
    if (timer) {
      return
    }

    obj.call(args)
  }

  obj.now = (...args) => {
    clear()
    run(...args)
  }

  obj.cancel = () => {
    clear()
  }

  return obj
}