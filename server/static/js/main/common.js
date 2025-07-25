App.ls_storage = `storage_v1`

App.SECOND = 1000
App.MINUTE = App.SECOND * 60
App.HOUR = App.MINUTE * 60
App.DAY = App.HOUR * 24
App.MONTH = App.DAY * 30
App.YEAR = App.DAY * 365

App.startup = () => {
  App.get_storage()
  App.setup_keyboard()
  App.setup_mouse()

  DOM.ev(document, `DOMContentLoaded`, () => {
    if (App.init) {
      App.init()
    }
  })
}

App.setup_keyboard = () => {
  DOM.ev(document, `keydown`, (e) => {
    if (App.settings_open()) {
      return
    }

    let n = 0

    if (e.code.startsWith(`Digit`)) {
      n = parseInt(e.code.replace(`Digit`, ``), 10)
    }
    else if (e.code.startsWith(`Numpad`)) {
      n = parseInt(e.code.replace(`Numpad`, ``), 10)
    }

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

            if (e.shiftKey) {
              App.auxclick(buttons[n - 1])
            }
            else {
              buttons[n - 1].click()
            }
          }
        }
      }
    }
    else if (e.key === `m`) {
      if (e.ctrlKey && !e.shiftKey) {
        if (Msg.msg && Msg.msg.any_open()) {
          // Do nothing
        }
        else {
          e.preventDefault()
          App.setup_menu_opts(true)
        }
      }
    }
    else if (e.key === `ArrowLeft`) {
      if (e.ctrlKey && !e.shiftKey) {
        App.prev_post()
      }
    }
    else if (e.key === `ArrowRight`) {
      if (e.ctrlKey && !e.shiftKey) {
        App.next_post()
      }
      else if (e.ctrlKey && e.shiftKey) {
        App.random_post()
      }
    }
    else if (e.key === `ArrowUp`) {
      if (e.ctrlKey && !e.shiftKey) {
        App.fresh_post()
      }
    }
  })
}

App.setup_mouse = () => {
  DOM.ev(document, `mousedown`, (e) => {
    if (e.button === 1) {
      e.preventDefault()
    }
  })
}

App.singplural = (what, length) => {
  if (length === 1) {
    return what
  }

  return `${what}s`
}

App.shuffle_array = (array) => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]]
  }

  return array
}

App.copy_to_clipboard = (text) => {
  navigator.clipboard.writeText(text)
}

App.select_all = (el) => {
  let selection = window.getSelection()
  let range = document.createRange()
  range.selectNodeContents(el)
  selection.removeAllRanges()
  selection.addRange(range)
}

App.is_lossless_image = (file) => {
  let allowed = [
    `image/jpeg`,
  ]

  return App.is_image(file) && !allowed.includes(file.type)
}

App.is_lossless_audio = (file) => {
  let allowed = [
    `audio/mpeg`,
  ]

  return App.is_audio(file) && !allowed.includes(file.type)
}

App.is_lossless_video = (file) => {
  let allowed = [
    `video/mp4`,
    `video/webm`,
  ]

  return App.is_video(file) && !allowed.includes(file.type)
}

App.is_image = (file, include_gif = true) => {
  let ok = file.type.match(`image/*`)

  if (ok) {
    if (!include_gif) {
      return !file.type.match(`image/gif`)
    }
  }

  return ok
}

App.is_audio = (file) => {
  return file.type.match(`audio/*`)
}

App.is_video = (file) => {
  return file.type.match(`video/*`)
}

App.set_css_var = (name, value) => {
  document.documentElement.style.setProperty(`--${name}`, value)
}

App.print_info = (msg) => {
  // eslint-disable-next-line no-console
  console.log(msg)
}

App.print_error = (msg) => {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}

App.contains_url = (text) => {
  let tlds = [
    `com`, `org`, `net`, `io`, `me`,
    `tv`, `gov`, `edu`, `info`, `co`,
  ]

  return text.match(/(https?:\/\/|www\.)\S+/gi) ||
  text.match(new RegExp(`\\b\\w+\\.(${tlds.join(`|`)})\\b`, `gi`))
}

App.prompt_text = (args = {}) => {
  new Promptext(args)
}

App.popmsg = (message, callback) => {
  new Popmsg(message, callback)
}

App.pophtml = (message, callback) => {
  new Popmsg(message, callback, true)
}

App.remove_multiple_empty_lines = (s) => {
  return s.replace(/\n\s*\n/g, `\n\n`)
}

App.capitalize = (s) => {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

App.ignore_buttons = (name, ignore) => {
  for (let g of ignore) {
    let el = DOM.el(`#${name}_opts_${g}`)

    if (el) {
      el.remove()
    }
  }
}

App.setup_menu_opts = (show = false, ignore = []) => {
  let name = `menu`

  App.make_opts(name, () => {
    App.ignore_buttons(name, ignore)

    App.bind_button(`${name}_opts_upload`, () => {
      App.location(`/`)
    }, () => {
      App.open_tab(`/`)
    }, App.icon(`upload`))

    App.bind_button(`${name}_opts_fresh`, () => {
      App.location(`/fresh`)
    }, () => {
      App.open_tab(`/fresh`)
    }, App.icon(`fresh`))

    App.bind_button(`${name}_opts_random`, () => {
      App.setup_random_opts(true, name)
    }, () => {
      App.random_post()
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_list`, () => {
      App.setup_list_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_admin`, () => {
      App.setup_admin_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_links`, () => {
      App.setup_link_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_you`, () => {
      App.setup_you_opts(App.user_id, true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_login`, () => {
      App.location(`/login`)
    }, () => {
      App.open_tab(`/login`)
    })

    App.bind_button(`${name}_opts_register`, () => {
      App.location(`/register`)
    }, () => {
      App.open_tab(`/register`)
    })
  }, show)
}

App.setup_you_opts = (user_id, show = false, parent = ``) => {
  let name = `you`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/list/posts?user_id=${user_id}`)
    }, undefined, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/list/reactions?user_id=${user_id}`)
    }, undefined, App.icon(`reactions`))

    App.bind_button(`${name}_opts_edit_name`, () => {
      App.edit_name()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_edit_password`, () => {
      App.edit_password()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_edit_settings`, () => {
      App.show_settings()
    }, undefined, App.icon(`settings`))

    App.bind_button(`${name}_opts_logout`, () => {
      let confirm_args = {
        message: `Visne profecto discedere`,
        callback_yes: () => {
          App.location(`/logout`)
        },
      }

      App.confirmbox(confirm_args)
    }, undefined, App.icon(`logout`))
  }, show, parent)
}

App.setup_sort_opts = (show = false) => {
  let name = `sort`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_asc_all`, () => {
      App.sort_action(App.sort_what, false, false)
    }, undefined, App.icon(`asc`, false))

    App.bind_button(`${name}_opts_desc_all`, () => {
      App.sort_action(App.sort_what, true)
    }, undefined, App.icon(`desc`))

    App.bind_button(`${name}_opts_asc_page`, () => {
      App.sort_action(App.sort_what, false, true)
    }, undefined, App.icon(`asc`, false))

    App.bind_button(`${name}_opts_desc_page`, () => {
      App.sort_action(App.sort_what, true, true)
    }, undefined, App.icon(`desc`))
  }, show)
}

App.setup_user_opts = (show = false, parent = ``) => {
  let name = `user`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id

      if (App.mode.includes(`admin`)) {
        App.location(`/admin/posts?user_id=${user_id}`)
      }
      else {
        App.location(`/list/posts?user_id=${user_id}`)
      }
    }, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id

      if (App.mode.includes(`admin`)) {
        App.open_tab(`/admin/posts?user_id=${user_id}`)
      }
      else {
        App.open_tab(`/list/posts?user_id=${user_id}`)
      }
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id

      if (App.mode.includes(`admin`)) {
        App.location(`/admin/reactions?user_id=${user_id}`)
      }
      else {
        App.location(`/list/reactions?user_id=${user_id}`)
      }
    }, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id

      if (App.mode.includes(`admin`)) {
        App.open_tab(`/admin/reactions?user_id=${user_id}`)
      }
      else {
        App.open_tab(`/list/reactions?user_id=${user_id}`)
      }
    }, App.icon(`reactions`))

    App.bind_button(`${name}_opts_user`, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id
      App.location(`/edit_user/${user_id}`)
    }, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id
      App.open_tab(`/edit_user/${user_id}`)
    }, App.icon(`edit`))
  }, show, parent)
}

App.fill_def_args = (def, args) => {
  for (let key in def) {
    if ((args[key] === undefined) && (def[key] !== undefined)) {
      args[key] = def[key]
    }
  }
}

App.confirmbox = (args = {}) => {
  new Confirmbox(args)
}

App.setup_reaction_opts = (show = false) => {
  let name = `reaction`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_edit`, () => {
      let id = App.active_item.dataset.id
      App.react_prompt(id)
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_delete`, () => {
      let id = App.active_item.dataset.id
      App.delete_reaction(id)
    }, undefined, App.icon(`delete`))
  }, show)
}

App.regex_u = (c, n) => {
  return `${c}{${n}}`
}

App.regex_t = (c, n) => {
  let u = App.regex_u(c, n)
  return `(?:(?!${u}|\\s).)`
}

App.regex_t2 = (c, n) => {
  let u = App.regex_u(c, n)
  return `(?:(?!${u}).)`
}

App.char_regex_1 = (char, n = 1) => {
  let c = App.escape_regex(char)
  let u = App.regex_u(c, n)
  let t = App.regex_t(c, n)
  let t2 = App.regex_t2(c, n)
  let regex = `${u}(${t}${t2}*${t}|${t})${u}`
  return new RegExp(regex, `g`)
}

App.char_regex_2 = (char, n = 1) => {
  let c = App.escape_regex(char)
  let u = App.regex_u(c, n)
  let t = App.regex_t(c, n)
  let regex = `(?:^|\\s)${u}(${t}.*?${t}|${t})${u}(?:$|\\s)`
  return new RegExp(regex, `g`)
}

App.char_regex_3 = (char, n = 1) => {
  let c = App.escape_regex(char)
  let u = App.regex_u(c, n)
  let t2 = App.regex_t2(c, n)
  let regex = `${u}(${t2}+)${u}`
  return new RegExp(regex, `g`)
}

App.to_bold = (text) => {
  return `<span class="md_highlight">${text}</span>`
}

App.parse_markdown = (text) => {
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

  action(App.char_regex_3(`\``), App.to_bold)
  action(App.char_regex_3(`"`), App.to_bold, true)
  action(App.char_regex_1(`*`, 2), App.to_bold)
  action(App.char_regex_1(`*`), App.to_bold)
  action(App.char_regex_2(`_`, 2), App.to_bold)
  action(App.char_regex_2(`_`), App.to_bold)
  return text
}

App.escape_regex = (s) => {
  return s.replace(/[^A-Za-z0-9]/g, `\\$&`)
}

App.create_debouncer = (func, delay) => {
  if (typeof func !== `function`) {
    App.print_error(`Invalid debouncer function`)
    return
  }

  if ((typeof delay !== `number`) || (delay < 1)) {
    App.print_error(`Invalid debouncer delay`)
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

App.replace_urls = (text) => {
  let here = window.location.origin
  let re = new RegExp(`${here}/post/([0-9A-Za-z]+)/?$`, `g`)
  text = text.replace(re, `/post/$1`)
  re = /https?:\/\/([a-z]{2,3})\.wikipedia\.org\/wiki\/([0-9A-Za-z_()#-]+)\/?$/g
  text = text.replace(re, `/wiki/$2`)
  re = /https?:\/\/www\.youtube\.com\/watch\?v=([0-9A-Za-z_-]+)\/?$/g
  text = text.replace(re, `/yt/$1`)
  re = /https?:\/\/youtu\.be\/([0-9A-Za-z_-]+)\/?$/g
  text = text.replace(re, `/yt/$1`)
  re = /https?:\/\/github\.com\/([0-9A-Za-z_-]+)\/([0-9A-Za-z_-]+)\/?$/g
  return text.replace(re, `/github/$1/$2`)
}

App.safe_html = (text) => {
  text = text.replace(/</g, `&lt;`)
  return text.replace(/>/g, `&gt;`)
}

App.text_html = (text, markdown = true) => {
  // Remove < and > to prevent XSS
  text = App.safe_html(text)

  // Markdown
  if (markdown) {
    text = App.parse_markdown(text)
  }

  // Internal posts
  let re = new RegExp(`/post/([0-9A-Za-z]+)`, `gi`)
  text = text.replace(re, `<a href="/post/$1">Post: $1</a>`)

  // Wikipedia
  re = /\/wiki\/([0-9A-Za-z_()-]+)(#[0-9A-Za-z_()-]+)?\/?/gi

  text = text.replace(re, (match, g1, g2) => {
    let u = g1
    let s = decodeURIComponent(g1)

    if (g2) {
      u += g2
      s += decodeURIComponent(g2)
    }

    return `<a href="https://wikipedia.org/wiki/${u}">Wiki: ${s}</a>`
  })

  // YouTube
  re = /\/yt\/([0-9A-Za-z_-]+)\/?/gi
  text = text.replace(re, `<a href="https://www.youtube.com/watch?v=$1">YT: $1</a>`)

  // GitHub
  re = /\/github\/([0-9A-Za-z_-]+)\/([0-9A-Za-z_-]+)\/?/gi
  text = text.replace(re, `<a href="https://github.com/$1/$2">GH: $1/$2</a>`)

  // :image_names:
  re = /:(\w+):/gi
  text = text.replace(re, `<img src="/static/icons/$1.gif" class="reaction_icon" title="$1">`)

  return text
}

App.user_mod_input = (what, o_value, vtype, callback) => {
  let repeat = false

  if (vtype === `password`) {
    repeat = true
  }

  function send(value) {
    if (vtype === `password`) {
      vtype = `string`
    }

    if (vtype === `number`) {
      value = parseInt(value)

      if (isNaN(value)) {
        value = 0
      }
    }

    if (o_value && (value === o_value)) {
      return
    }

    if (callback) {
      callback(what, value, vtype)
    }
    else {
      App.mod_user(what, value, vtype)
    }
  }

  let name = what.split(`_`).join(` `)

  let prompt_args = {
    value: o_value,
    placeholder: `Type the new ${name}`,
    max: App.max_reaction_length,
    password: vtype === `password`,
    callback: (value_1) => {
      if (!repeat) {
        send(value_1)
        return
      }

      let prompt_args_2 = {
        placeholder: `Enter the value again`,
        max: App.max_reaction_length,
        password: vtype === `password`,
        callback: (value_2) => {
          if (value_1 !== value_2) {
            App.popmsg(`Values don't match`)
            return
          }

          send(value_2)
        },
      }

      App.prompt_text(prompt_args_2)
    },
  }

  App.prompt_text(prompt_args)
}

App.edit_name = () => {
  App.user_mod_input(`name`, App.user_name, `string`, (what, value, vtype) => {
    App.do_user_edit(what, value, vtype, `Name`, () => {
      App.user_name = value
      DOM.el(`#user_name`).textContent = value
    })
  })
}

App.edit_password = () => {
  App.user_mod_input(`password`, ``, `password`, (what, value, vtype) => {
    App.do_user_edit(what, value, vtype, `Password`)
  })
}

App.do_user_edit = async (what, value, vtype, title, callback) => {
  let ids = [App.user_id]

  let response = await fetch(`/mod_user`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, what, value, vtype}),
  })

  if (response.ok) {
    App.popmsg(`${title} updated`, () => {
      if (callback) {
        callback()
      }
    })
  }
  else {
    App.print_error(response.status)
  }
}

App.setup_list_opts = (show = false, parent = ``) => {
  let name = `list`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/list/posts`)
    }, () => {
      App.open_tab(`/list/posts`)
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/list/reactions`)
    }, () => {
      App.open_tab(`/list/reactions`)
    }, App.icon(`reactions`))
  }, show, parent)
}

App.setup_random_opts = (show = false, parent = ``) => {
  let name = `random`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_any`, () => {
      App.location(`/random`)
    }, () => {
      App.open_tab(`/random`)
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_video`, () => {
      App.location(`/random_video`)
    }, () => {
      App.open_tab(`/random_video`)
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_audio`, () => {
      App.location(`/random_audio`)
    }, () => {
      App.open_tab(`/random_audio`)
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_image`, () => {
      App.location(`/random_image`)
    }, () => {
      App.open_tab(`/random_image`)
    }, App.icon(`random`))
  }, show, parent)
}

App.setup_admin_opts = (show = false, parent = ``) => {
  let name = `admin`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/admin/posts`)
    }, () => {
      App.open_tab(`/admin/posts`)
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/admin/reactions`)
    }, () => {
      App.open_tab(`/admin/reactions`)
    }, App.icon(`reactions`))

    App.bind_button(`${name}_opts_users`, () => {
      App.location(`/admin/users`)
    }, () => {
      App.open_tab(`/admin/users`)
    }, App.icon(`users`))
  }, show, parent)
}

App.setup_link_opts = (show = false, parent = ``) => {
  let name = `link`

  App.make_opts(name, () => {
    let c = DOM.el(`#links_container`)

    for (let [i, link] of App.links.entries()) {
      let item = DOM.create(`div`, `aero_button`, `${name}_opts_${i}`)
      item.textContent = link.name
      item.title = link.url
      c.appendChild(item)

      App.bind_button(`${name}_opts_${i}`, () => {
        App.open_tab(link.url, link.target)
      }, () => {
        App.open_tab(link.url)
      }, link.icon)
    }
  }, show, parent)
}

App.make_opts = (name, setup, show = false, parent = ``) => {
  let msg_name = `msg_${name}`

  if (App[msg_name]) {
    if (show) {
      App[msg_name].show()
    }

    return
  }

  App[msg_name] = Msg.factory({
    after_show: () => {
      let selection = window.getSelection()
      selection.removeAllRanges()
    },
  })

  let t = DOM.el(`#template_${name}_opts`)
  App[msg_name].set(t.innerHTML)
  setup()

  if (parent) {
    let c = DOM.el(`.dialog_container`, App[msg_name].content)
    let btn = DOM.create(`div`, `aero_button`, `${name}_opts_back`)
    btn.textContent = `Back`
    c.appendChild(btn)

    App.bind_button(`${name}_opts_back`, () => {
      App[`setup_${parent}_opts`](true)
    }, undefined, `<`)
  }

  if (show) {
    App[msg_name].show()
  }
}

App.make_msg = (name, title) => {
  let msg_name = `msg_${name}`

  if (App[msg_name]) {
    return App[msg_name]
  }

  let enable_titlebar

  if (title) {
    enable_titlebar = true
  }
  else {
    enable_titlebar = false
  }

  App[msg_name] = Msg.factory({
    enable_titlebar, window_x: `floating_right`, center_titlebar: true
  })

  App[msg_name].set(DOM.el(`#template_${name}`).innerHTML)

  if (title) {
    App[msg_name].set_title(title)
  }
}

App.bind_button = (what, func, mfunc, submenu = ``) => {
  let name = what.match(/^(.*?)_opts/)[1]
  let msg_name = `msg_${name}`
  let el = DOM.el(`#${what}`)

  if (!el) {
    return
  }

  let c = DOM.el(`.dialog_container`, App[msg_name].content)
  let btns = DOM.els(`.aero_button`, c)
  let numbers

  if (btns.length > 9) {
    numbers = false
  }
  else {
    numbers = true
  }

  let index = btns.indexOf(el)
  let otext = el.textContent
  el.textContent = ``

  let text = DOM.create(`div`, `aero_text`)

  if (numbers) {
    text.textContent = `${index + 1}. ${otext}`
  }
  else {
    text.textContent = otext
  }

  el.appendChild(text)

  if (submenu && App.show_menu_icons) {
    let sub = DOM.create(`div`, `aero_arrow menu_icon`)
    sub.textContent = submenu
    el.appendChild(sub)
  }

  if (func) {
    DOM.ev(el, `click`, (e) => {
      App[msg_name].close()
      func()
    })
  }

  if (mfunc || func) {
    DOM.ev(el, `auxclick`, (e) => {
      if (e.button === 1) {
        App[msg_name].close()

        if (mfunc) {
          mfunc()
        }
        else if (func) {
          func()
        }
      }
    })
  }

  DOM.ev(el, `contextmenu`, (e) => {
    App[msg_name].close()
    e.preventDefault()

    if (func) {
      func()
    }
  })
}

App.encode_uri = (uri) => {
  return encodeURIComponent(uri)
}

App.setup_edit_post_opts = (show = false) => {
  let name = `edit_post`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_title`, () => {
      App.edit_title()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_description`, () => {
      App.edit_description()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_filename`, () => {
      App.edit_filename()
    }, undefined, App.icon(`filename`))

    App.bind_button(`${name}_opts_privacy`, () => {
      App.setup_edit_privacy_opts(true, name)
    }, undefined, App.icon(App.post.privacy))

    App.bind_button(`${name}_opts_delete`, () => {
      let confirm_args = {
        message: `Delete this post`,
        callback_yes: () => {
          App.delete_post()
        },
      }

      App.confirmbox(confirm_args)
    }, undefined, App.icon(`delete`))
  }, show)
}

App.setup_edit_privacy_opts = (show = false, parent = ``) => {
  let name = `edit_privacy`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_public`, () => {
      App.edit_privacy(`public`)
    }, undefined, App.icon(`public`))

    App.bind_button(`${name}_opts_private`, () => {
      App.edit_privacy(`private`)
    }, undefined, App.icon(`private`))
  }, show, parent)
}

App.prev_post = (blank = false) => {
  let url

  if (App.post.name) {
    url = `/prev/${App.post.name}`
  }
  else {
    url = `/random`
  }

  App.goto_url(url, blank)
}

App.next_post = (blank = false) => {
  let url

  if (App.post.name) {
    url = `/next/${App.post.name}`
  }
  else {
    url = `/random`
  }

  App.goto_url(url, blank)
}

App.fresh_post = () => {
  App.location(`/fresh`)
}

App.random_post = () => {
  App.location(`/random`)
}

App.msg_show = (what) => {
  let msg = App[`msg_${what}`]

  if (msg) {
    msg.show()
  }
}

App.modal_open = () => {
  return Msg.msg && Msg.msg.any_open()
}

App.settings_open = () => {
  return App.msg_settings && App.msg_settings.is_open()
}

App.open_tab = (url, target = `_blank`) => {
  window.open(url, target)
}

App.location = (where) => {
  window.location = where
}

App.goto_url = (url, new_tab = false) => {
  if (new_tab) {
    App.open_tab(url)
  }
  else {
    App.location(url)
  }
}

App.close_modals = () => {
  Msg.msg.close_all()
}

App.timeago = (date) => {
  let level = 0
  let diff = Date.now() - date
  let places = 1
  let result

  if (diff < App.MINUTE) {
    result = `just now`
    level = 1
  }
  else if (diff < App.HOUR) {
    let n = parseFloat((diff / App.MINUTE).toFixed(places))

    if (n === 1) {
      result = `${n} min ago`
    }
    else {
      result = `${n} mins ago`
    }

    level = 2
  }
  else if ((diff >= App.HOUR) && (diff < App.DAY)) {
    let n = parseFloat(diff / App.HOUR).toFixed(places)

    if (n === 1) {
      result = `${n} hr ago`
    }
    else {
      result = `${n} hrs ago`
    }

    level = 3
  }
  else if ((diff >= App.DAY) && (diff < App.MONTH)) {
    let n = parseFloat(diff / App.DAY).toFixed(places)

    if (n === 1) {
      result = `${n} day ago`
    }
    else {
      result = `${n} days ago`
    }

    level = 4
  }
  else if ((diff >= App.MONTH) && (diff < App.YEAR)) {
    let n = parseFloat(diff / App.MONTH).toFixed(places)

    if (n === 1) {
      result = `${n} month ago`
    }
    else {
      result = `${n} months ago`
    }

    level = 5
  }
  else if (diff >= App.YEAR) {
    let n = parseFloat(diff / App.YEAR).toFixed(places)

    if (n === 1) {
      result = `${n} year ago`
    }
    else {
      result = `${n} years ago`
    }

    level = 6
  }

  return [result, level]
}

App.login_feedback = () => {
  App.pophtml(`You might need to <a href="/login">login</a> or <a href="/register">register</a>`)
}

App.to_top = () => {
  window.scrollTo(0, 0)
}

App.to_bottom = () => {
  window.scrollTo(0, document.body.scrollHeight)
}

App.flash = (text) => {
  App.msg_flash = Msg.factory({
    close_on_overlay_click: false,
    window_x: `none`,
    class: `blue`,
  })

  App.msg_flash.set(text)
  App.msg_flash.show()
}

App.close_flash = () => {
  if (App.msg_flash) {
    App.msg_flash.close()
  }
}

App.icon = (what) => {
  return App[`icon_for_${what}`]
}

App.get_storage = () => {
  let storage = localStorage.getItem(App.ls_storage)
  let obj

  if (storage) {
    obj = JSON.parse(storage)
  }
  else {
    obj = {}
  }

  App.storage = obj
}

App.save_storage = () => {
  localStorage.setItem(App.ls_storage, JSON.stringify(App.storage))
}

App.storage_value = (what, fallback) => {
  let value = App.storage[what]

  if (value === undefined) {
    return fallback
  }

  return value
}

App.auxclick = (el) => {
  let event = new MouseEvent(`auxclick`, {
    bubbles: true,
    cancelable: true,
    button: 1,
  })

  el.dispatchEvent(event)
}

App.no_mod = (e) => {
  return !e.ctrlKey && !e.shiftKey
}

App.setup_post_edit_opts = (show = false) => {
  let name = `post_edit`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_title`, () => {
      App.edit_post_title()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_public`, () => {
      App.edit_post_privacy(`public`)
    }, undefined, App.icon(`public`))

    App.bind_button(`${name}_opts_private`, () => {
      App.edit_post_privacy(`private`)
    }, undefined, App.icon(`private`))
  }, show)
}

App.setup_user_edit_opts = (show = false) => {
  let name = `user_edit`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_poster_no`, () => {
      App.mod_user(`poster`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reader_no`, () => {
      App.mod_user(`reader`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reader_yes`, () => {
      App.mod_user(`reader`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_lister_no`, () => {
      App.mod_user(`lister`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_lister_yes`, () => {
      App.mod_user(`lister`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_reacter_no`, () => {
      App.mod_user(`reacter`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reacter_yes`, () => {
      App.mod_user(`reacter`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_mage_no`, () => {
      App.mod_user(`mage`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_mage_yes`, () => {
      App.mod_user(`mage`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_admin_no`, () => {
      App.mod_user(`admin`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_admin_yes`, () => {
      App.mod_user(`admin`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_rpm`, () => {
      App.user_mod_input(`rpm`, ``, `number`)
    })

    App.bind_button(`${name}_opts_max_size`, () => {
      App.user_mod_input(`max_size`, ``, `number`)
    })

    App.bind_button(`${name}_opts_mark`, () => {
      App.user_mod_input(`mark`, ``, `string`)
    })

    App.bind_button(`${name}_opts_name`, () => {
      App.user_mod_input(`name`, ``, `string`)
    })

    App.bind_button(`${name}_opts_username`, () => {
      App.user_mod_input(`username`, ``, `string`)
    })

    App.bind_button(`${name}_opts_password`, () => {
      App.user_mod_input(`password`, ``, `password`)
    })
  }, show)
}

App.double_confirm = (message, func, confirmed = false) => {
  let yes

  if (confirmed) {
    yes = `Yes!`
  }
  else {
    yes = `Yes`
  }

  let confirm_args = {
    yes,
    message,
    callback_yes: () => {
      if (confirmed) {
        func()
      }
      else {
        App.double_confirm(message, func, true)
      }
    },
  }

  App.confirmbox(confirm_args)
}

App.get_youtube_id = (url) => {
  let v_id = false
  let list_id = false

  let split = url.split(/(vi\/|v%3D|v=|\/v\/|youtu\.be\/|\/embed\/|\/live\/)/)
  let id = undefined !== split[2] ? split[2].split(/[^0-9a-z_-]/i)[0] : split[0]

  v_id = id.length === 11 ? id : false

  let list_match = url.match(/(?:\?|&)(list=[0-9A-Za-z_-]+)/)
  let index_match = url.match(/(?:\?|&)(index=[0-9]+)/)

  if (list_match) {
    list_id = list_match[1].replace(`list=`, ``)
  }

  if (list_id && !v_id) {
    let index = 0

    if (index_match) {
      index = parseInt(index_match[1].replace(`index=`, ``)) - 1
    }

    return [`list`, [list_id, index]]
  }
  else if (v_id) {
    return [`video`, v_id]
  }
}

App.is_a_url = (s) => {
  if (s.includes(` `)) {
    return false
  }

  if (s.startsWith(`http://`) || s.startsWith(`https://`)) {
    if (s.length <= (s.indexOf(`://`) + 3)) {
      return false
    }

    if (s.endsWith(`]`)) {
      return false
    }
    else if (s.endsWith(`"`)) {
      return false
    }
    else if (s.endsWith(`'`)) {
      return false
    }

    return true
  }

  return false
}

App.urlize = (text) => {
  let re = /(\bhttps?:\/\/\S+)/gi
  return text.replace(re, `<a href="$1">$1</a>`)
}

App.untab_string = (s) => {
  s = s.replace(/\t/gm, `  `)
  let lines = s.split(`\n`)

  if (lines.length <= 1) {
    return s
  }

  let ns = []
  let pos = -1

  for (let line of lines) {
    if (!line.trim()) {
      continue
    }

    let m = line.match(/^\s+/)

    if (m) {
      let n = m[0].length

      if ((pos === -1) || (n < pos)) {
        pos = n
      }

      ns.push(n)
    }
    else {
      return s
    }
  }

  let new_lines = []
  let spaces = ``

  for (let i = 0; i < pos; i++) {
    spaces += ` `
  }

  for (let line of lines) {
    let re = new RegExp(`(^${spaces})`)
    new_lines.push(line.replace(re, ``))
  }

  return new_lines.join(`\n`)
}

App.is_ascii_art = (text) => {
  // If text is very short, it's unlikely to be ASCII art
  if (!text || (text.length < 20)) {
    return false
  }

  // If it contains URLs returl false
  let url_regex = /https?:\/\/[^\s]+/gi

  if (url_regex.test(text)) {
    return false
  }

  let lines = text.split(`\n`)

  // ASCII art usually has multiple lines
  if (lines.length < 3) {
    return false
  }

  // Check line length consistency
  let line_lengths = lines.map(line => line.length)
  let avg_line_length = line_lengths.reduce((a, b) => a + b, 0) / line_lengths.length
  let line_dev = line_lengths.map(len => Math.abs(len - avg_line_length))
  let avg_dev = line_dev.reduce((a, b) => a + b, 0) / line_dev.length

  // Character distribution analysis
  let total_chars = text.length
  let alpha_chars = (text.match(/[a-zA-Z]/g) || []).length

  // eslint-disable-next-line no-useless-escape
  let special_chars = (text.match(/[/\\|(){}\[\]<>*#-_+=^~`]/g) || []).length

  // Calculate key ratios
  let alpha_ratio = alpha_chars / total_chars
  let special_ratio = special_chars / total_chars
  let line_consistency = 1 - (avg_dev / avg_line_length)

  // Scoring system
  let score = 0

  // High special character ratio indicates ASCII art
  if (special_ratio > 0.15) {
    score += 2
  }

  // Low alphabetic character ratio indicates ASCII art
  if (alpha_ratio < 0.4) {
    score += 2
  }

  // Consistent line lengths indicate ASCII art
  if (line_consistency > 0.8) {
    score += 2
  }

  // ASCII art usually has longer lines
  if (avg_line_length > 30) {
    score += 1
  }

  // Multiple lines are common in ASCII art
  if (lines.length > 5) {
    score += 1
  }

  // Threshold can be adjusted based on testing
  return score >= 4
}

App.size_string = (bytes) => {
  if (bytes < 1024) {
    return `${bytes} b`
  }

  let kb = bytes / 1024

  if (kb < 1024) {
    return `${kb.toFixed(1)} kb`
  }

  let mb = kb / 1024

  if (mb < 1024) {
    return `${mb.toFixed(1)} mb`
  }

  let gb = mb / 1024

  if (gb < 1024) {
    return `${gb.toFixed(1)} gb`
  }

  let tb = gb / 1024
  return `${tb.toFixed(1)} tb`
}

App.feedback = async (response) => {
  let json = await App.json(response)

  if (json && json.message) {
    App.popmsg(json.message)
  }
  else if (response.statusText) {
    App.popmsg(response.statusText)
  }
}

App.json = async (response) => {
  return await response.json().catch(() => ({}))
}

App.num_lines = (text) => {
  return text.split(`\n`).length
}

App.is_filename = (str) => {
  str = str.toLowerCase().trim()

  if (!str) {
    return false
  }

  // Contains
  if (!/^[a-z0-9_.-]+$/.test(str)) {
    return false
  }

  // Starts with
  if (!/^[a-z0-9]/.test(str)) {
    return false
  }

  // Ends with
  if (!/[a-z0-9]$/.test(str)) {
    return false
  }

  // Check that it contains at least 1 dot
  if (str.indexOf(`.`) < 1) {
    return false
  }

  // Check if it contains dots in succession
  if (str.includes(`..`)) {
    return false
  }

  return true
}

App.reload = () => {
  window.location.reload()
}

App.change_menu_icon = (what, value) => {
  let menu_item = DOM.el(`#${what}`)
  let icon = DOM.el(`.menu_icon`, menu_item)
  icon.textContent = value
}

App.show_settings = () => {
  let created = App.msg_settings !== undefined

  if (!created) {
    App.make_msg(`settings`, `Settings`)
  }

  App.msg_settings.show()

  if (!created) {
    let select = DOM.el(`#settings_theme`)

    for (let theme of App.themes) {
      let option = DOM.create(`option`)
      option.value = theme[0]
      option.textContent = theme[1]
      select.appendChild(option)
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

App.get_cookie = (name) => {
  let cookie = document.cookie.split(`;`).find(c => c.trim().startsWith(`${name}=`))
  return cookie ? cookie.split(`=`)[1] : null
}

App.set_cookie = (name, value, days = 900) => {
  let expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString()
  document.cookie = `${name}=${value}; expires=${expires}; path=/`
}

App.clear_cookie = (name) => {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
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
    let cycles = Array.from(select.options).map(option => option.value)

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