App.setup_keyboard = () => {
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
    }
    else if (e.key === `m`) {
      if (e.ctrlKey && !e.shiftKey) {
        if (Msg.msg && Msg.msg.any_open()) {
          // Do nothing
        }
        else {
          e.preventDefault()
          let show_return = vars.mode !== `index`
          setup_explore_opts(show_return, true)
        }
      }
    }
    else if (e.key === `ArrowRight`) {
      if (e.ctrlKey && !e.shiftKey) {
        next_post()
      }
      else if (e.ctrlKey && e.shiftKey) {
        random_post()
      }
    }
    else if (e.key === `ArrowUp`) {
      if (e.ctrlKey && !e.shiftKey) {
        fresh_post()
      }
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

App.is_image = (file) => {
  return file.type.match(`image/*`)
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
  return text.match(/(https?:\/\/|www\.)\S+/gi)
}

App.prompt_text = (args = {}) => {
  a = new Promptext(args)
}

App.popmsg = (message, callback) => {
  new Popmsg(message, callback)
}

App.remove_multiple_empty_lines = (s) => {
  return s.replace(/\n\s*\n/g, `\n\n`)
}

App.capitalize = (s) => {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

App.setup_explore_opts = (show_return = true, show = false) => {
  let name = `explore`

  make_opts(name, () => {
    if (!show_return) {
      DOM.el(`#${name}_opts_return`).remove()
    }

    bind_button(`${name}_opts_fresh`, () => {
      window.location = `/fresh`
    }, () => {
      open_tab(`/fresh`)
    })

    bind_button(`${name}_opts_random`, () => {
      window.location = `/random`
    }, () => {
      open_tab(`/random`)
    })

    bind_button(`${name}_opts_return`, () => {
      window.location = `/`
    }, () => {
      open_tab(`/`)
    })

    bind_button(`${name}_opts_you`, () => {
      setup_you_opts(vars.user_id, true)
    })

    bind_button(`${name}_opts_list`, () => {
      setup_list_opts(true)
    })

    bind_button(`${name}_opts_admin`, () => {
      setup_admin_opts(true)
    })

    bind_button(`${name}_opts_links`, () => {
      setup_link_opts(true)
    })
  }, show)
}

App.setup_you_opts = (user_id, show = false) => {
  let name = `you`

  make_opts(name, () => {
    bind_button(`${name}_opts_posts`, () => {
      window.location = `/list/posts?user_id=${user_id}`
    })

    bind_button(`${name}_opts_reactions`, () => {
      window.location = `/list/reactions?user_id=${user_id}`
    })

    bind_button(`${name}_opts_edit_name`, () => {
      edit_name()
    })

    bind_button(`${name}_opts_edit_password`, () => {
      edit_password()
    })

    bind_button(`${name}_opts_logout`, () => {
      let confirm_args = {
        message: `Visne profecto discedere ?`,
        callback_yes: () => {
          window.location = `/logout`
        },
      }

      confirmbox(confirm_args)
    })
  }, show)
}

App.setup_user_opts = (show = false) => {
  let name = `user`

  make_opts(name, () => {
    bind_button(`${name}_opts_posts`, () => {
      let user_id = vars.user_opts_user_id

      if (vars.mode.includes(`admin`)) {
        window.location = `/admin/posts?user_id=${user_id}`
      }
      else {
        window.location = `/list/posts?user_id=${user_id}`
      }
    }, () => {
      let user_id = vars.user_opts_user_id

      if (vars.mode.includes(`admin`)) {
        open_tab(`/admin/posts?user_id=${user_id}`)
      }
      else {
        open_tab(`/list/posts?user_id=${user_id}`)
      }
    })

    bind_button(`${name}_opts_reactions`, () => {
      let user_id = vars.user_opts_user_id

      if (vars.mode.includes(`admin`)) {
        window.location = `/admin/reactions?user_id=${user_id}`
      }
      else {
        window.location = `/list/reactions?user_id=${user_id}`
      }
    }, () => {
      let user_id = vars.user_opts_user_id

      if (vars.mode.includes(`admin`)) {
        open_tab(`/admin/reactions?user_id=${user_id}`)
      }
      else {
        open_tab(`/list/reactions?user_id=${user_id}`)
      }
    })

    bind_button(`${name}_opts_user`, () => {
      let user_id = vars.user_opts_user_id
      window.location = `/edit_user/${user_id}`
    }, () => {
      let user_id = vars.user_opts_user_id
      open_tab(`/edit_user/${user_id}`)
    })
  }, show)
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

  make_opts(name, () => {
    bind_button(`${name}_opts_edit`, () => {
      let id = vars.active_item.dataset.id
      react_prompt(id)
    })

    bind_button(`${name}_opts_delete`, () => {
      let id = vars.active_item.dataset.id
      delete_reaction(id)
    })
  }, show)
}

App.regex_u = (c, n) => {
  return `${c}{${n}}`
}

App.regex_t = (c, n) => {
  let u = regex_u(c, n)
  return `(?:(?!${u}|\\s).)`
}

App.regex_t2 = (c, n) => {
  let u = regex_u(c, n)
  return `(?:(?!${u}).)`
}

App.char_regex_1 = (char, n = 1) => {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t = regex_t(c, n)
  let t2 = regex_t2(c, n)
  let regex = `${u}(${t}${t2}*${t}|${t})${u}`
  return new RegExp(regex, `g`)
}

App.char_regex_2 = (char, n = 1) => {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t = regex_t(c, n)
  let regex = `(?:^|\\s)${u}(${t}.*?${t}|${t})${u}(?:$|\\s)`
  return new RegExp(regex, `g`)
}

App.char_regex_3 = (char, n = 1) => {
  let c = escape_regex(char)
  let u = regex_u(c, n)
  let t2 = regex_t2(c, n)
  let regex = `${u}(${t2}+)${u}`
  return new RegExp(regex, `g`)
}

to_bold = (text) => {
  return `<span class='md_highlight'>${text}</span>`
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

  action(char_regex_3(`\``), to_bold)
  action(char_regex_3(`"`), to_bold, true)
  action(char_regex_1(`*`, 2), to_bold)
  action(char_regex_1(`*`), to_bold)
  action(char_regex_2(`_`, 2), to_bold)
  action(char_regex_2(`_`), to_bold)
  return text
}

App.escape_regex = (s) => {
  return s.replace(/[^A-Za-z0-9]/g, `\\$&`)
}

App.create_debouncer = (func, delay) => {
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

App.text_html = (text, markdown = true) => {
  // Remove < and > to prevent XSS
  text = text.replace(/</g, `&lt;`)
  text = text.replace(/>/g, `&gt;`)

  // Markdown
  if (markdown) {
    text = parse_markdown(text)
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
      mod_user(what, value, vtype)
    }
  }

  let prompt_args = {
    value: o_value,
    placeholder: `Type the new ${what}`,
    max: vars.text_reaction_length,
    password: vtype === `password`,
    callback: (value_1) => {
      if (!repeat) {
        send(value_1)
        return
      }

      let prompt_args_2 = {
        placeholder: `Enter the value again`,
        max: vars.text_reaction_length,
        password: vtype === `password`,
        callback: (value_2) => {
          if (value_1 !== value_2) {
            popmsg(`Values don't match`)
            return
          }

          send(value_2)
        },
      }

      prompt_text(prompt_args_2)
    },
  }

  prompt_text(prompt_args)
}

App.edit_name = () => {
  user_mod_input(`name`, vars.user_name, `string`, (what, value, vtype) => {
    do_user_edit(what, value, vtype, `Name`, () => {
      vars.user_name = value
      DOM.el(`#user_name`).textContent = value
    })
  })
}

App.edit_password = () => {
  user_mod_input(`password`, ``, `password`, (what, value, vtype) => {
    do_user_edit(what, value, vtype, `Password`)
  })
}

App.do_user_edit = async (what, value, vtype, title, callback) => {
  let ids = [vars.user_id]

  let response = await fetch(`/mod_user`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, what, value, vtype}),
  })

  if (response.ok) {
    popmsg(`${title} updated`, () => {
      if (callback) {
        callback()
      }
    })
  }
  else {
    print_error(response.status)
  }
}

App.setup_list_opts = (show = false) => {
  let name = `list`

  make_opts(name, () => {
    bind_button(`${name}_opts_posts`, () => {
      window.location = `/list/posts`
    }, () => {
      open_tab(`/list/posts`)
    })

    bind_button(`${name}_opts_reactions`, () => {
      window.location = `/list/reactions`
    }, () => {
      open_tab(`/list/reactions`)
    })
  }, show)
}

App.setup_admin_opts = (show = false) => {
  let name = `admin`

  make_opts(name, () => {
    bind_button(`${name}_opts_posts`, () => {
      window.location = `/admin/posts`
    }, () => {
      open_tab(`/admin/posts`)
    })

    bind_button(`${name}_opts_reactions`, () => {
      window.location = `/admin/reactions`
    }, () => {
      open_tab(`/admin/reactions`)
    })

    bind_button(`${name}_opts_users`, () => {
      window.location = `/admin/users`
    }, () => {
      open_tab(`/admin/users`)
    })
  }, show)
}

App.setup_link_opts = (show = false) => {
  let name = `link`

  make_opts(name, () => {
    let c = DOM.el(`#links_container`)

    for (let [i, link] of vars.links.entries()) {
      let item = DOM.create(`div`, `aero_button`, `${name}_opts_${i}`)
      item.textContent = link.name
      item.title = link.url
      c.appendChild(item)

      bind_button(`${name}_opts_${i}`, () => {
        open_tab(link.url, link.target)
      }, () => {
        open_tab(link.url)
      })
    }
  }, show)
}

App.make_opts = (name, setup, show = false) => {
  let msg_name = `msg_${name}_opts`

  if (vars[msg_name]) {
    if (show) {
      vars[msg_name].show()
    }

    return
  }

  vars[msg_name] = Msg.factory({
    after_show: () => {
      let selection = window.getSelection()
      selection.removeAllRanges()
    },
  })

  let t = DOM.el(`#template_${name}_opts`)
  vars[msg_name].set(t.innerHTML)
  setup()

  if (show) {
    vars[msg_name].show()
  }
}

App.bind_button = (what, func, mfunc) => {
  let name = what.split(`_`)[0]
  let msg_name = `msg_${name}_opts`
  let el = DOM.el(`#${what}`)

  if (!el) {
    return
  }

  let c = DOM.el(`.dialog_container`, vars[msg_name].content)
  let btns = DOM.els(`.aero_button`, c)
  let index = btns.indexOf(el)
  el.textContent = `${index + 1}. ${el.textContent}`

  if (func) {
    DOM.ev(el, `click`, (e) => {
      vars[msg_name].close()
      func()
    })
  }

  if (mfunc || func) {
    DOM.ev(el, `auxclick`, (e) => {
      if (e.button === 1) {
        vars[msg_name].close()

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
    vars[msg_name].close()
    e.preventDefault()

    if (func) {
      func()
    }
  })
}

App.open_tab = (url, target = `_blank`) => {
  window.open(url, target)
}

App.encode_uri = (uri) => {
  return encodeURIComponent(uri)
}

App.setup_editpost_opts = (show = false) => {
  let name = `editpost`

  make_opts(name, () => {
    bind_button(`${name}_opts_title`, () => {
      edit_title()
    })

    bind_button(`${name}_opts_delete`, () => {
      let confirm_args = {
        message: `Delete this post ?`,
        callback_yes: () => {
          delete_post()
        },
      }

      confirmbox(confirm_args)
    })
  }, show)
}

App.next_post = () => {
  if (vars.name) {
    window.location = `/next/${vars.name}`
  }
  else {
    window.location = `/random`
  }
}

App.fresh_post = () => {
  window.location = `/fresh`
}

App.random_post = () => {
  window.location = `/random`
}