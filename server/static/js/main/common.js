App.ls_storage = `storage_v1`
App.corner_msg_delay = 6200

App.SECOND = 1000
App.MINUTE = App.SECOND * 60
App.HOUR = App.MINUTE * 60
App.DAY = App.HOUR * 24
App.MONTH = App.DAY * 30
App.YEAR = App.DAY * 365
App.DECADE = App.YEAR * 10
App.CENTURY = App.YEAR * 100
App.MILLENNIUM = App.YEAR * 1000

App.LETTERS = [`a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`, `i`, `j`, `k`, `l`, `m`, `n`, `o`, `p`, `q`, `r`, `s`, `t`, `u`, `v`, `w`, `x`, `y`, `z`]

App.startup = () => {
  App.get_storage()
  App.setup_keyboard()
  App.setup_mouse()

  DOM.ev(document, `DOMContentLoaded`, () => {
    if (App.init) {
      App.init()
      App.check_cmd()
    }
  })
}

App.setup_keyboard = () => {
  DOM.ev(document, `keydown`, (e) => {
    if (App.settings_open()) {
      return
    }

    let n = -1

    if (e.code.startsWith(`Digit`)) {
      n = parseInt(e.code.replace(`Digit`, ``), 10)
    }
    else if (e.code.startsWith(`Numpad`)) {
      n = parseInt(e.code.replace(`Numpad`, ``), 10)
    }
    else if (e.code.startsWith(`Key`)) {
      let letter = e.code.replace(`Key`, ``).toLowerCase()

      if ((letter >= `a`) && (letter <= `z`)) {
        n = 10 + App.LETTERS.indexOf(letter)
      }
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
      else if (App.any_modal_open()) {
        let pmt = Promptext.instance

        if (pmt && pmt.is_open()) {
          if (pmt.args.multi) {
            if (e.shiftKey || e.ctrlKey) {
              pmt.submit(e.shiftKey || e.ctrlKey)
              e.preventDefault()
            }
          }
          else {
            pmt.submit(e.shiftKey || e.ctrlKey)
            e.preventDefault()
          }
        }
        else {
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
    }
    else if (!isNaN(n) && (n > -1)) {
      if (App.any_modal_open()) {
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
        if (App.any_modal_open()) {
          // Do nothing
        }
        else {
          e.preventDefault()
          App.setup_menu_opts(true)
        }
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
      if (App.mode === `post`) {
        if (e.ctrlKey && e.shiftKey) {
          App.edit_post()
        }
        else if (App.image_expanded) {
          App.scroll_modal_up()
        }
        else if (App.msg_image && App.msg_image.is_open()) {
          App.expand_modal_image()
        }
      }
      else if (e.ctrlKey && !e.shiftKey) {
        App.fresh_post()
      }
    }
    else if (e.key === `ArrowDown`) {
      if (App.mode === `post`) {
        if (e.ctrlKey && !e.shiftKey) {
          if (!Popmsg.instance || !Popmsg.instance.msg.is_open()) {
            App.react_prompt()
          }
        }
        else if (App.image_expanded) {
          App.scroll_modal_down()
        }
        else if (App.msg_image && App.msg_image.is_open()) {
          App.expand_modal_image()
        }
      }
    }
    else if (e.key === `.`) {
      if (e.ctrlKey && !e.shiftKey) {
        App.show_video_commands()
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
    `audio/ogg`,
    `audio/opus`,
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

App.get_css_var = (name) => {
  let value = getComputedStyle(document.documentElement).getPropertyValue(`--${name}`)

  if (value) {
    return value.trim()
  }
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
    enable_titlebar,
    window_x: `floating_right`,
    center_titlebar: true,
    after_show: () => {
      App.current_msg = msg_name
    },
  })

  App[msg_name].set(DOM.el(`#template_${name}`).innerHTML)

  if (title) {
    App[msg_name].set_title(title)
  }
}

App.bind_button = (args = {}) => {
  let def_args = {
    icon: ``,
    close: true,
    class: ``,
  }

  App.fill_def_args(def_args, args)
  let name = args.what.match(/^(.*?)_opts/)[1]
  let msg_name = `msg_${name}`
  let el = DOM.el(`#${args.what}`)

  if (!el) {
    return
  }

  let btn_cls = ``

  if (args.class) {
    btn_cls = App.cleanlist(args.class)
  }

  let c = DOM.el(`.dialog_container`, App[msg_name].content)
  let btns = DOM.els(`.aero_button`, c)
  let numbers

  if (btns.length > 30) {
    numbers = false
  }
  else {
    numbers = true
  }

  let index = btns.indexOf(el)
  let otext = el.textContent
  el.textContent = ``

  let text = DOM.create(`div`, `aero_text`)
  let text_label = DOM.create(`div`, `button_text_label`)
  text_label.textContent = otext
  let current_letter = 0

  if (numbers) {
    let text_num = DOM.create(`div`, `button_text_number`)

    if (index <= 8) {
      text_num.textContent = `${index + 1}.`
    }
    else {
      text_num.textContent = `${App.LETTERS[current_letter]}.`
      current_letter += 1
    }

    text.append(text_num)
  }

  text.append(text_label)
  el.appendChild(text)

  if (btn_cls) {
    for (let cls of btn_cls) {
      el.classList.add(cls)
    }
  }

  if (args.icon && App.show_menu_icons) {
    let sub = DOM.create(`div`, `aero_arrow menu_icon`)
    sub.textContent = args.icon
    el.appendChild(sub)
  }

  if (args.func) {
    DOM.ev(el, `click`, (e) => {
      if (args.close) {
        App[msg_name].close()
      }

      args.func()
    })
  }

  if (args.mfunc || args.func) {
    DOM.ev(el, `auxclick`, (e) => {
      if (e.button === 1) {
        if (args.close) {
          App[msg_name].close()
        }

        if (args.mfunc) {
          args.mfunc()
        }
        else if (args.func) {
          args.func()
        }
      }
    })
  }

  DOM.ev(el, `contextmenu`, (e) => {
    if (args.close) {
      App[msg_name].close()
    }

    e.preventDefault()

    if (args.func) {
      args.func()
    }
  })
}

App.encode_uri = (uri) => {
  return encodeURIComponent(uri)
}

App.next_post = (new_tab = false) => {
  App.next_action(`any`, new_tab)
}

App.fresh_post = () => {
  App.location(`/fresh`)
}

App.random_post = () => {
  let path = `/random`
  App.location(path)

  App.storage.cmd = {
    kind: `random`,
    value: path,
    date: Date.now(),
  }

  App.save_storage()
}

App.msg_show = (what, back_button = true) => {
  let msg = App[`msg_${what}`]

  if (msg) {
    let back = DOM.el(`#${what}_opts_back`)

    if (back) {
      if (back_button) {
        DOM.show(back)
      }
      else {
        DOM.hide(back)
      }
    }

    msg.show()
  }
}

App.modal_open = () => {
  return App.any_modal_open()
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

    if (n < 10) {
      if (n === 1) {
        result = `${n} year ago`
      }
      else {
        result = `${n} years ago`
      }

      level = 6
    }
    else if (diff < App.CENTURY) {
      n = parseFloat(diff / App.DECADE).toFixed(places)

      if (n === 1) {
        result = `${n} decade ago`
      }
      else {
        result = `${n} decades ago`
      }

      level = 7
    }
    else if (diff < App.MILLENNIUM) {
      n = parseFloat(diff / App.CENTURY).toFixed(places)

      if (n === 1) {
        result = `${n} century ago`
      }
      else {
        result = `${n} centuries ago`
      }

      level = 8
    }
    else {
      n = parseFloat(diff / App.MILLENNIUM).toFixed(places)

      if (n === 1) {
        result = `${n} millennium ago`
      }
      else {
        result = `${n} millennia ago`
      }

      level = 9
    }
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

App.msgbox = (value, mode = `text`) => {
  if (!App.msg_info) {
    App.msg_info = Msg.factory({
      after_show: () => {
        App.current_msg = `msgbox`
      },
    })

    let t = DOM.el(`#template_msgbox`)
    App.msg_info.set(t.innerHTML)
  }

  let c = DOM.el(`#msgbox`)

  if (mode === `text`) {
    c.textContent = value
  }
  else if (mode === `html`) {
    c.innerHTML = ``
    c.append(value)
  }

  App.msg_info.show()
}

App.flash = (text) => {
  App.msg_flash = Msg.factory({
    close_on_overlay_click: false,
    window_x: `none`,
    class: `blue`,
    after_show: () => {
      App.current_msg = `flash`
    },
  })

  App.msg_flash.show(text)
}

App.close_flash = () => {
  if (App.msg_flash) {
    App.msg_flash.close()
  }
}

App.icon = (what) => {
  return App.icons[what]
}

App.media_icon = (what) => {
  return App.media_icons[what]
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

App.random_action = (what, new_tab = false) => {
  if (App.random_mode === `page`) {
    what = what === `random` ? `` : what
    App.do_random_page(what, new_tab)
    return
  }

  let path

  if (what === `any`) {
    path = `/random`
  }
  else {
    path = `/random/${what}`
  }

  App.storage.cmd = {
    kind: `random`,
    value: path,
    date: Date.now(),
  }

  App.save_storage()

  if (new_tab) {
    App.open_tab(path)
  }
  else {
    App.location(path)
  }
}

App.next_action = (what, new_tab = false) => {
  if (!App.post) {
    return
  }

  let post_id = App.post.id

  if (!post_id) {
    return
  }

  let base_path = what === `any` ? `/next` : `/next/${what}`
  let url = new URL(base_path, window.location.origin)
  url.searchParams.set(`post_id`, post_id)
  let path = url.pathname + url.search

  App.storage.cmd = {
    kind: `next`,
    value: path,
    date: Date.now(),
  }

  App.save_storage()

  if (new_tab) {
    App.open_tab(path)
  }
  else {
    App.location(path)
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

App.show_random = (what = `menu`, back_button = true) => {
  App.random_mode = what
  App.setup_random_opts(false, `menu`)
  App.msg_show(`random`, back_button)
}

App.show_next = (what = `menu`, back_button = false) => {
  App.setup_next_opts(false, `menu`)
  App.msg_show(`next`, back_button)
}

App.any_modal_open = () => {
  return Msg.msg && Msg.msg.any_open()
}

App.viewport_height = () => {
  return Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
}

App.prompt_search = (what) => {
  let where

  if (App.is_admin) {
    where = `admin`
  }
  else {
    where = `list`
  }

  function get_path(query) {
    return `/${where}/${what}?query=${encodeURIComponent(query)}`
  }

  let prompt_args = {
    placeholder: `Enter search term`,
    max: 250,
    callback: (query) => {
      let path = get_path(query)
      App.goto_url(path)
    },
    alt_callback: (query) => {
      let path = get_path(query)
      App.open_tab(path)
    },
  }

  App.prompt_text(prompt_args)
}

App.is_disabled = (el) => {
  return el.classList.contains(`strike`) || el.disabled
}

App.corner_msg = (args = {}) => {
  let def_args = {
    mode: `normal`,
    delay: 5000,
    on_middle_click: () => {},
  }

  App.fill_def_args(def_args, args)

  if (!App.msg_corner) {
    App.msg_corner = Msg.factory({
      id: `corner_msg`,
      preset: `popup_autoclose`,
      position: `bottomright`,
      autoclose_delay: args.delay,
      on_click: () => {
        args.on_click()
      },
      on_middle_click: () => {
        args.on_middle_click()
      },
      after_show: () => {
        App.current_msg = `corner`
      },
      zStack_level: 52000000,
    })
  }

  App.corner_mode = args.mode
  App.msg_corner.options.on_click = args.on_click
  App.msg_corner.show(args.text)
}

App.hide_corner_msg = () => {
  if (App.msg_corner) {
    App.msg_corner.close()
  }
}

App.check_cmd = () => {
  if (!App.storage.cmd) {
    return false
  }

  let now = Date.now()

  if ((now - App.storage.cmd.date) > (App.SECOND * 10)) {
    return false
  }

  App.corner_msg({
    text: `Click to do this again`,
    delay: App.corner_msg_delay,
    on_click: () => {
      App.run_cmd()
    },
  })
}

App.run_cmd = () => {
  let path

  if (App.storage.cmd.kind === `next`) {
    if (!App.post) {
      return
    }

    let post_id = App.post.id

    if (!post_id) {
      return
    }

    let base_path = App.storage.cmd.value
    let url = new URL(base_path, window.location.origin)
    url.searchParams.set(`post_id`, post_id)
    path = url.pathname + url.search
  }
  else {
    path = App.storage.cmd.value
  }

  App.storage.cmd.date = Date.now()
  App.save_storage()
  App.location(path)
}

App.clamp = (value, max, min) => {
  if (value > max) {
    return max
  }
  else if (value < min) {
    return min
  }

  return value
}

App.cleanlist = (cls) => {
  return cls.match(/\S+/g) || []
}

App.button_highlight = (what, add = true) => {
  let item = DOM.el(`#${what}`)

  if (item) {
    if (add) {
      item.classList.add(`button_highlight`)
    }
    else {
      item.classList.remove(`button_highlight`)
    }
  }
}

App.blink = (el) => {
  el.classList.add(`blink`)

  setTimeout(() => {
    el.classList.remove(`blink`)
  }, 1000)
}