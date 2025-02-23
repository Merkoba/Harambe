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
  let def_args = {
    placeholder: `Enter Text`,
    max: 0,
    multi: false,
    value: ``,
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

  input.rows = 6
  input.id = `prompt_input`
  input.type = `text`
  input.placeholder = args.placeholder
  input.value = args.value
  let btn = DOM.create(`div`)
  btn.id = `prompt_submit`
  btn.textContent = `Submit`
  c.appendChild(input)
  c.appendChild(btn)
  msg.set(c)

  function submit() {
    args.callback(input.value)
    msg.close()
  }

  function update_btn() {
    if (args.max > 0) {
      btn.textContent = `Submit (${input.value.length}/${args.max})`
    }
    else {
      btn.textContent = `Submit (${input.value.length})`
    }
  }

  DOM.ev(input, `input`, (e) => {
    if (args.max > 0) {
      if (input.value.length > args.max) {
        input.value = input.value.substring(0, args.max).trim()
      }
    }

    update_btn()
  })

  DOM.ev(input, `keydown`, (e) => {
    if (e.key === `Enter`) {
      if (args.multi) {
        if (e.shiftKey || e.ctrlKey) {
          submit()
          e.preventDefault()
        }
      }
      else {
        submit()
        e.preventDefault()
      }
    }
  })

  DOM.ev(btn, `click`, submit)
  update_btn()
  msg.show()
  input.focus()
}

function popmsg(message, callback) {
  let msg = Msg.factory({
    persistent: false,
    after_close: callback,
  })

  msg.show(message)
}

function remove_multiple_empty_lines(s) {
  return s.replace(/\n\s*\n/g, `\n\n`)
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function setup_admin_opts() {
  vars.msg_admin_opts = Msg.factory()
  let admin_opts = DOM.el(`#template_admin_opts`)
  vars.msg_admin_opts.set(admin_opts.innerHTML)

  DOM.ev(`#admin_opts_posts`, `click`, (e) => {
    vars.msg_admin_opts.close()
    window.location = `/admin/posts`
  })

  DOM.ev(`#admin_opts_reactions`, `click`, (e) => {
    vars.msg_admin_opts.close()
    window.location = `/admin/reactions`
  })

  DOM.ev(`#admin_opts_users`, `click`, (e) => {
    vars.msg_admin_opts.close()
    window.location = `/admin/users`
  })

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
  let explore_opts = DOM.el(`#template_explore_opts`)
  vars.msg_explore_opts.set(explore_opts.innerHTML)

  DOM.ev(`#explore_opts_fresh`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/fresh`
  })

  DOM.ev(`#explore_opts_posts`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/posts`
  })

  DOM.ev(`#explore_opts_reactions`, `click`, (e) => {
    vars.msg_explore_opts.close()
    window.location = `/reactions`
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
  let you_opts = DOM.el(`#template_you_opts`)
  vars.msg_you_opts.set(you_opts.innerHTML)

  DOM.ev(`#you_opts_posts`, `click`, (e) => {
    vars.msg_you_opts.close()
    window.location = `/posts?username=${username}`
  })

  DOM.ev(`#you_opts_reactions`, `click`, (e) => {
    vars.msg_you_opts.close()
    window.location = `/reactions?username=${username}`
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
  let user_opts = DOM.el(`#template_user_opts`)
  vars.msg_user_opts.set(user_opts.innerHTML)

  function get_name() {
    if (vars.mode.includes(`post`)) {
      return vars.active_item.dataset.uploader
    }
    else if (vars.mode.includes(`reaction`)) {
      return vars.active_item.dataset.uname
    }
  }

  DOM.ev(`#user_opts_posts`, `click`, (e) => {
    vars.msg_user_opts.close()

    if (vars.mode.includes(`_history`)) {
      let name = get_name()
      window.location = `/posts?query=${name}`
    }
    else {
      let username = vars.active_item.dataset.username
      window.location = `/admin/posts?username=${username}`
    }
  })

  DOM.ev(`#user_opts_reactions`, `click`, (e) => {
    vars.msg_user_opts.close()

    if (vars.mode.includes(`_history`)) {
      let name = get_name()
      window.location = `/reactions?query=${name}`
    }
    else {
      let username = vars.active_item.dataset.username
      window.location = `/admin/reactions?username=${username}`
    }
  })
}

function fill_def_args(def, args) {
  for (let key in def) {
    if ((args[key] === undefined) && (def[key] !== undefined)) {
      args[key] = def[key]
    }
  }
}

function confirmbox(args = {}) {
  let def_args = {
    message: `Are you sure ?`,
    yes: `Yes`,
    no: `No`,
  }

  fill_def_args(def_args, args)

  let msg = Msg.factory({
    persistent: false,
  })

  let c = DOM.create(`div`)
  c.id = `confirmbox_container`
  let m = DOM.create(`div`)
  m.id = `confirmbox_message`
  m.textContent = args.message
  let btns = DOM.create(`div`)
  btns.id = `confirmbox_buttons`
  let y = DOM.create(`div`, `aero_button`)
  y.textContent = args.yes
  let n = DOM.create(`div`, `aero_button`)
  n.textContent = args.no
  c.appendChild(m)
  btns.appendChild(n)
  btns.appendChild(y)
  c.appendChild(btns)
  msg.set(c)

  DOM.ev(y, `click`, (e) => {
    if (args.callback_yes) {
      args.callback_yes()
    }

    msg.close()
  })

  DOM.ev(n, `click`, (e) => {
    if (args.callback_no) {
      args.callback_no()
    }

    msg.close()
  })

  msg.show()
}