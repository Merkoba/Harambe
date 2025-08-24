App.fade_delay = 100
App.fade_delay_fast = 25
App.fade_step = 0.02
App.audio_context = null
App.pitch_node = null
App.reverb_node = null
App.reverb_enabled = false
App.bass_node = null
App.treble_node = null
App.bass_boost_enabled = false
App.bass_cut_enabled = false
App.treble_boost_enabled = false
App.treble_cut_enabled = false
App.current_audio_source = null
App.playback_step = 0.05
App.jump_popup_delay = 5000
App.rotate_popup_delay = 5000
App.automatic_popup_delay = 5000
App.auto_video_on = false
App.REVERB_DEFAULT_MIX = 0.55 // default wet mix when enabling reverb

App.toggle_commands = () => {
  if (App.multimedia_embed()) {
    if (App.msg_video_commands && App.msg_video_commands.is_open()) {
      App.msg_video_commands.close()
    }
    else {
      App.show_video_commands()
    }
  }
  else if (App.image_embed()) {
    if (App.msg_image_commands && App.msg_image_commands.is_open()) {
      App.msg_image_commands.close()
    }
    else {
      App.show_image_commands()
    }
  }
}

App.show_commands = () => {
  if (App.multimedia_embed()) {
    App.show_video_commands()
  }
  else if (App.image_embed()) {
    App.show_image_commands()
  }
}

App.show_video_commands = () => {
  App.setup_video_commands_opts(true)
}

App.show_image_commands = () => {
  App.setup_image_commands_opts(true)
}

App.video_jump = (feedback = false) => {
  let video = App.get_video()

  if (video) {
    if (video.paused) {
      App.video_jump_enabled = true
      video.play()
    }
    else {
      App.video_jump_action(feedback)
    }
  }
}

App.video_jump_action = (feedback = false) => {
  App.video_jump_enabled = false
  let video = App.get_video()

  if (video) {
    let duration = video.duration

    if (duration > 0) {
      let min = parseInt(0.1 * duration)
      let max = parseInt(0.9 * duration)
      let random_time = App.random_int({min, max})
      video.currentTime = random_time

      if (feedback) {
        App.corner_msg({
          text: `Jumped to ${parseInt(random_time)}s`,
          delay: App.jump_popup_delay,
          on_click: () => {
            App.video_jump_action()
          },
        })
      }
    }
  }
}

App.video_rewind = (seconds = 0) => {
  let video = App.get_video()

  if (!video) {
    return
  }

  let volume = video.volume

  function action() {
    video.currentTime = 0

    setTimeout(() => {
      video.volume = volume
      video.play()
    }, 200)
  }

  if (seconds > 0) {
    video.currentTime -= seconds
    video.play()
  }
  else if (video.paused) {
    action()
  }
  else {
    App.video_fade_out_fast(() => {
      action()
    })
  }
}

App.update_playback_title = (mode) => {
  let video = App.get_video()

  if (video) {
    let playback = video.playbackRate.toFixed(2).replace(/\.?0+$/, ``)
    let speed = DOM.el(`#speed_menu_title`)
    let pitch = DOM.el(`#pitch_menu_title`)

    if (speed) {
      if (mode === `speed`) {
        speed.innerText = `Speed: ${playback}x`
      }
      else {
        speed.innerText = `Speed`
      }
    }

    if (pitch) {
      if (mode === `pitch`) {
        pitch.innerText = `Pitch: ${playback}x`
      }
      else {
        pitch.innerText = `Pitch`
      }
    }
  }
}

App.playback_change = (mode, action) => {
  let video = App.get_video()

  if (!video) {
    return
  }

  let rate

  if (App.playback_rate_mode !== mode) {
    rate = 1.0
  }
  else {
    rate = video.playbackRate
  }

  if (action === `increase`) {
    rate = Math.min(10, rate + App.playback_step)
  }
  else if (action === `decrease`) {
    rate = Math.max(0.1, rate - App.playback_step)
  }

  App.set_video_playback(rate, mode)
  App.update_playback_title(mode)
  App.playback_rate_mode = mode
}

App.increase_playback = (mode) => {
  App.playback_change(mode, `increase`)
}

App.decrease_playback = (mode) => {
  App.playback_change(mode, `decrease`)
}

App.video_slower = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.decrease_playback(`speed`)
  }
}

App.video_faster = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.increase_playback(`speed`)
  }
}

App.video_speed_reset = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.set_video_playback(1.0, `speed`)
    App.update_playback_title(`speed`)
  }
}

App.set_video_playback = (value, mode) => {
  let video = App.get_video()

  if (video) {
    video.playbackRate = value

    if (value === 1.0) {
      App.button_highlight(`video_commands_opts_speed`, false)
      App.button_highlight(`video_commands_opts_pitch`, false)
    }
    else if (mode === `speed`) {
      App.button_highlight(`video_commands_opts_pitch`, false)
      App.button_highlight(`video_commands_opts_speed`, true)
    }
    else if (mode === `pitch`) {
      App.button_highlight(`video_commands_opts_speed`, false)
      App.button_highlight(`video_commands_opts_pitch`, true)
    }
  }
}

App.video_fade_in = () => {
  let video = App.get_video()

  if (video) {
    video.volume = 0
    video.play()

    let fadeIn = setInterval(() => {
      if (video.volume < 1) {
        video.volume = Math.min(1, video.volume + App.fade_step)
      }
      else {
        clearInterval(fadeIn)
      }
    }, App.fade_delay)
  }
}

App.video_fade_out = (callback) => {
  let video = App.get_video()

  if (video) {
    let fadeOut = setInterval(() => {
      if (video.volume > 0) {
        video.volume = Math.max(0, video.volume - App.fade_step)
      }
      else {
        clearInterval(fadeOut)
        video.pause()

        if (callback) {
          callback()
        }
      }
    }, App.fade_delay)
  }
}

App.video_fade_out_fast = (callback) => {
  let video = App.get_video()

  if (video) {
    let fadeOut = setInterval(() => {
      if (video.volume > 0) {
        video.volume = Math.max(0, video.volume - App.fade_step)
      }
      else {
        clearInterval(fadeOut)
        video.pause()

        if (callback) {
          callback()
        }
      }
    }, App.fade_delay_fast)
  }
}

App.init_audio_context = () => {
  if (App.audio_context) {
    return true
  }

  try {
    App.audio_context = new (window.AudioContext || window.webkitAudioContext)()
    App.create_reverb_node()
    App.create_bass_node()
    App.create_treble_node()
    let video = App.get_video()

    if (video) {
      App.setup_audio_context(video)
    }

    return true
  }
  catch (e) {
    return false
  }
}

App.setup_audio_context = (video) => {
  if (!App.init_audio_context()) {
    return false
  }

  if (App.audio_context.state === `suspended`) {
    App.audio_context.resume()
  }

  if (!App.pitch_node || (video.audioSource !== App.current_audio_source)) {
    try {
      if (App.current_audio_source) {
        App.current_audio_source.disconnect()
      }

      let source = App.audio_context.createMediaElementSource(video)
      App.current_audio_source = source
      App.pitch_node = App.audio_context.createGain()

      source.connect(App.pitch_node)
      App.pitch_node.connect(App.bass_node.input)
      App.bass_node.output.connect(App.treble_node.input)
      App.treble_node.output.connect(App.reverb_node.input)
      App.reverb_node.output.connect(App.audio_context.destination)
      video.audioSource = source
    }
    catch (e) {
      if (e.name === `InvalidStateError`) {
        return true
      }

      return false
    }
  }

  return true
}

App.video_pitch_up = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(false)
    App.increase_playback(`pitch`)
  }
}

App.video_pitch_down = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(false)
    App.decrease_playback(`pitch`)
  }
}

App.video_pitch_reset = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.set_video_playback(1.0, `pitch`)
    App.update_playback_title(`pitch`)
  }
}

App.set_video_preserve_pitch = (value) => {
  let video = App.get_video()

  if (video) {
    try {
      if (`preservesPitch` in video) {
        video.preservesPitch = value
      }

      if (`mozPreservesPitch` in video) {
        video.mozPreservesPitch = value
      }

      if (`webkitPreservesPitch` in video) {
        video.webkitPreservesPitch = value
      }
    }
    catch (e) {
      App.print_error(`Could not set pitch flag:`, e)
    }
  }
}

App.create_reverb_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let ac = App.audio_context
    let convolver = ac.createConvolver()
    let dry_gain = ac.createGain()
    let wet_gain = ac.createGain()
    // Node to sum the final output of the effect chain
    let effect_sum_gain = ac.createGain()
    // A new gain node for the bypass signal
    let bypass_gain = ac.createGain()
    // The final output node that collects signal from either the effect or bypass
    let output_gain = ac.createGain()

    let pre_delay = ac.createDelay(1.0)
    pre_delay.delayTime.value = 0.03

    let lowpass = ac.createBiquadFilter()
    lowpass.type = `lowpass`
    lowpass.frequency.value = 10 * 1000
    lowpass.Q.value = 0.7

    let comp = ac.createDynamicsCompressor()
    comp.threshold.value = -18
    comp.knee.value = 20
    comp.ratio.value = 2
    comp.attack.value = 0.003
    comp.release.value = 0.25

    let ir_rms = App.create_impulse_response(convolver) || 1.0

    convolver.normalize = true
    dry_gain.gain.value = 1.0
    wet_gain.gain.value = 0.0
    effect_sum_gain.gain.value = 1.0
    output_gain.gain.value = 1.0

    // *** Key Change: Set the bypass to be active by default ***
    bypass_gain.gain.value = 1.0 // Pass signal through
    effect_sum_gain.gain.value = 0.0 // Mute the effect chain output

    App.reverb_node = {
      input: ac.createGain(),
      convolver,
      pre_delay,
      lowpass,
      dry: dry_gain,
      wet: wet_gain,
      sum: effect_sum_gain,
      bypass: bypass_gain,
      comp,
      output: output_gain,
      impulse_rms: ir_rms,
      last_mix: 0,
      is_active: false,
    }

    let reverb = App.reverb_node

    // --- Wiring ---

    // 1. Input splits to the effect chain AND the bypass chain
    reverb.input.connect(reverb.dry)
    reverb.input.connect(reverb.pre_delay)
    reverb.input.connect(reverb.bypass)

    // 2. The original effect chain wiring
    reverb.pre_delay.connect(reverb.convolver)
    reverb.convolver.connect(reverb.lowpass)
    reverb.lowpass.connect(reverb.wet)
    reverb.wet.connect(reverb.comp)
    reverb.comp.connect(reverb.sum)
    reverb.dry.connect(reverb.sum)

    // 3. Both the effect chain's output and the bypass chain's output connect to the final output
    reverb.sum.connect(reverb.output)
    reverb.bypass.connect(reverb.output)

    // --- Control Methods ---

    reverb.enable = () => {
      // Use setTargetAtTime for smooth, click-free transitions
      let now = App.audio_context.currentTime
      reverb.bypass.gain.setTargetAtTime(0.0, now, 0.01)
      reverb.sum.gain.setTargetAtTime(1.0, now, 0.01)
      reverb.is_active = true
    }

    reverb.disable = () => {
      let now = App.audio_context.currentTime
      reverb.bypass.gain.setTargetAtTime(1.0, now, 0.01)
      reverb.sum.gain.setTargetAtTime(0.0, now, 0.01)
      reverb.is_active = false
    }
  }
  catch (e) {
    App.print_error(`Could not create reverb node:`, e)
  }
}

App.create_impulse_response = (convolver) => {
  try {
    let ac = App.audio_context
    let sample_rate = ac.sampleRate

    let seconds = 3.0
    let length = Math.floor(sample_rate * seconds)
    let impulse = ac.createBuffer(2, length, sample_rate)

    let early_times = [0.007, 0.013, 0.021, 0.033]
    let early_gains = [0.6, 0.45, 0.32, 0.22]

    for (let channel = 0; channel < 2; channel++) {
      let data = impulse.getChannelData(channel)

      for (let j = 0; j < early_times.length; j++) {
        let t = early_times[j] + (channel === 0 ? 0.000 : 0.0015)
        let idx = Math.floor(t * sample_rate)
        if (idx < length) {
          let gain = early_gains[j]

          for (let k = -8; k <= 8; k++) {
            let p = idx + k

            if ((p >= 0) && (p < length)) {
              let window = 1 - Math.abs(k) / 8
              data[p] += gain * window * 0.04
            }
          }
        }
      }

      let decay = 3.5

      for (let i = 0; i < length; i++) {
        let t = i / length
        let env = Math.pow(1 - t, decay)
        let noise = ((Math.random() * 2) - 1) * env * 0.6
        data[i] += noise
      }

      for (let i = Math.floor(length * 0.85); i < length; i++) {
        let fade = (length - i) / (length * 0.15)
        data[i] *= fade
      }
    }

    // Compute RMS of impulse for makeup gain compensation
    let sum_sq = 0
    let total_samples = 0

    for (let c = 0; c < impulse.numberOfChannels; c++) {
      let data = impulse.getChannelData(c)
      total_samples += data.length

      for (let i = 0; i < data.length; i++) {
        let v = data[i]
        sum_sq += v * v
      }
    }

    let rms = Math.sqrt(sum_sq / Math.max(1, total_samples)) || 1.0
    convolver.buffer = impulse
    return rms
  }
  catch (e) {
    App.print_error(`Could not create impulse response:`, e)
    return 1.0
  }
}

App.create_bass_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let ac = App.audio_context
    let input_gain = ac.createGain()
    let effect_output_gain = ac.createGain()
    let bypass_gain = ac.createGain()
    let final_output_gain = ac.createGain()

    let bass_filter = ac.createBiquadFilter()
    bass_filter.type = `lowshelf`
    bass_filter.frequency.value = 320
    bass_filter.gain.value = 0
    bass_filter.Q.value = 1.0

    let highpass = ac.createBiquadFilter()
    highpass.type = `highpass`
    highpass.frequency.value = 40
    highpass.Q.value = 0.7

    // Default state: bypass is on, effect is off
    bypass_gain.gain.value = 1.0
    effect_output_gain.gain.value = 0.0

    App.bass_node = {
      input: input_gain,
      bass_filter,
      highpass,
      effect_output: effect_output_gain,
      bypass: bypass_gain,
      output: final_output_gain,
      is_active: false,
    }

    let bass = App.bass_node

    // --- Wiring ---

    // 1. Input splits to the effect chain AND the bypass chain
    bass.input.connect(bass.highpass)
    bass.input.connect(bass.bypass)

    // 2. Effect chain
    bass.highpass.connect(bass.bass_filter)
    bass.bass_filter.connect(bass.effect_output)

    // 3. Both paths connect to the final output
    bass.effect_output.connect(bass.output)
    bass.bypass.connect(bass.output)

    // --- Control Methods ---

    bass.enable = () => {
      let now = App.audio_context.currentTime
      bass.bypass.gain.setTargetAtTime(0.0, now, 0.01)
      bass.effect_output.gain.setTargetAtTime(1.0, now, 0.01)
      bass.is_active = true
    }

    bass.disable = () => {
      let now = App.audio_context.currentTime
      bass.bypass.gain.setTargetAtTime(1.0, now, 0.01)
      bass.effect_output.gain.setTargetAtTime(0.0, now, 0.01)
      bass.is_active = false
    }
  }
  catch (e) {
    App.print_error(`Could not create bass boost node:`, e)
  }
}

App.create_treble_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let ac = App.audio_context
    let input_gain = ac.createGain()
    let effect_output_gain = ac.createGain()
    let bypass_gain = ac.createGain()
    let final_output_gain = ac.createGain()

    let treble_filter = ac.createBiquadFilter()
    treble_filter.type = `highshelf`
    treble_filter.frequency.value = 3200
    treble_filter.gain.value = 0 // Starts at 0dB boost
    treble_filter.Q.value = 1.0

    // Note: This highpass might be redundant if you always chain after the bass boost
    let highpass = ac.createBiquadFilter()
    highpass.type = `highpass`
    highpass.frequency.value = 40
    highpass.Q.value = 0.7

    // Default state: bypass is on, effect is off
    bypass_gain.gain.value = 1.0
    effect_output_gain.gain.value = 0.0

    App.treble_node = {
      input: input_gain,
      treble_filter,
      highpass,
      effect_output: effect_output_gain,
      bypass: bypass_gain,
      output: final_output_gain,
      is_active: false,
    }

    let treble = App.treble_node

    // --- Wiring ---

    // 1. Input splits to the effect chain AND the bypass chain
    treble.input.connect(treble.highpass)
    treble.input.connect(treble.bypass)

    // 2. Effect chain
    treble.highpass.connect(treble.treble_filter)
    treble.treble_filter.connect(treble.effect_output)

    // 3. Both paths connect to the final output
    treble.effect_output.connect(treble.output)
    treble.bypass.connect(treble.output)

    // --- Control Methods ---

    treble.enable = () => {
      let now = App.audio_context.currentTime
      treble.bypass.gain.setTargetAtTime(0.0, now, 0.01)
      treble.effect_output.gain.setTargetAtTime(1.0, now, 0.01)
      treble.is_active = true
    }

    treble.disable = () => {
      let now = App.audio_context.currentTime
      treble.bypass.gain.setTargetAtTime(1.0, now, 0.01)
      treble.effect_output.gain.setTargetAtTime(0.0, now, 0.01)
      treble.is_active = false
    }
  }
  catch (e) {
    App.print_error(`Could not create treble boost node:`, e)
  }
}

App.set_bass_gain = (gain_db) => {
  if (!App.bass_node || !App.audio_context) {
    return
  }

  if (gain_db === 0) {
    App.button_highlight(`video_commands_opts_bass`, false)
  }
  else {
    App.button_highlight(`video_commands_opts_bass`)
  }

  if (gain_db === 0) {
    App.bass_node.disable()
    return
  }

  App.bass_node.enable()

  let ac = App.audio_context
  let now = ac.currentTime
  let clamped_gain = Math.max(-12, Math.min(12, gain_db))
  App.bass_node.bass_filter.gain.setTargetAtTime(clamped_gain, now, 0.01)
}

App.set_treble_gain = (gain_db) => {
  if (!App.treble_node || !App.audio_context) {
    return
  }

  if (gain_db === 0) {
    App.button_highlight(`video_commands_opts_treble`, false)
  }
  else {
    App.button_highlight(`video_commands_opts_treble`)
  }

  if (gain_db === 0) {
    App.treble_node.disable()
    return
  }

  App.treble_node.enable()

  let ac = App.audio_context
  let now = ac.currentTime
  let clamped_gain = Math.max(-12, Math.min(12, gain_db))
  App.treble_node.treble_filter.gain.setTargetAtTime(clamped_gain, now, 0.01)
}

App.set_reverb_mix = (mix) => {
  if (!App.reverb_node || !App.audio_context) {
    return
  }

  let ac = App.audio_context
  let node = App.reverb_node
  let clamped = Math.max(0, Math.min(1, mix))

  // Avoid redundant scheduling
  if (Math.abs(clamped - node.last_mix) < 0.002) {
    return
  }

  let now = ac.currentTime

  if (clamped === 0) {
    // When mix is zero, just disable the effect path.
    // The disable() method handles the crossfade to the bypass node correctly.
    node.disable()

    // We can still reset the internal gains for a clean state when the
    // reverb is re-enabled, but we must NOT interfere with the
    // sum.gain ramp that disable() has already started.
    node.dry.gain.cancelScheduledValues(now)
    node.wet.gain.cancelScheduledValues(now)

    node.dry.gain.setValueAtTime(1.0, now)
    node.wet.gain.setValueAtTime(0.0, now)
  }
  else {
    // If mix is greater than zero, ensure the effect path is active.
    node.enable()

    // Perceptual remap for mix control
    let percept = Math.pow(clamped, 0.6)
    let t = percept * Math.PI / 2
    let dry_level = Math.cos(t)
    let wet_level = Math.sin(t)

    // Energy compensation factoring IR RMS
    let ir_rms = node.impulse_rms || 1.0
    let total_level = Math.sqrt((dry_level * dry_level) + (wet_level * wet_level * ir_rms * ir_rms))
    let makeup_gain = 1.0 / Math.max(0.0001, total_level)
    makeup_gain = Math.max(0.5, Math.min(1.5, makeup_gain))

    let ramp_time = 0.03
    let end = now + ramp_time

    function ramp(param, value) {
      try {
        param.cancelScheduledValues(now)
        param.setValueAtTime(param.value, now)
        param.linearRampToValueAtTime(value, end)
      }
      catch (e) {
        param.setValueAtTime(value, end) // Fallback
      }
    }

    ramp(node.dry.gain, dry_level)
    ramp(node.wet.gain, wet_level)
    ramp(node.sum.gain, makeup_gain)
  }

  node.last_mix = clamped
}

App.video_reverb_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.reverb_node) {
      App.button_highlight(`video_commands_opts_reverb`)
      App.reverb_enabled = true
      App.set_reverb_mix(App.REVERB_DEFAULT_MIX)
    }
  }
}

App.video_reverb_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.reverb_node) {
      App.button_highlight(`video_commands_opts_reverb`, false)
      App.reverb_enabled = false
      App.set_reverb_mix(0.0)
    }
  }
}

App.video_reverb_toggle = () => {
  if (App.reverb_enabled) {
    App.video_reverb_off()
  }
  else {
    App.video_reverb_on()
  }
}

App.video_bass_boost_toggle = () => {
  App.video_bass_cut_off()

  if (App.bass_boost_enabled) {
    App.video_bass_boost_off()
  }
  else {
    App.video_bass_boost_on()
  }
}

App.video_bass_boost_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.bass_node) {
      App.button_highlight(`video_bass_opts_boost`)
      App.bass_boost_enabled = true
      App.set_bass_gain(6)
    }
  }
}

App.video_bass_boost_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.bass_node) {
      App.button_highlight(`video_bass_opts_boost`, false)
      App.bass_boost_enabled = false
      App.set_bass_gain(0)
    }
  }
}

App.video_bass_cut_toggle = () => {
  App.video_bass_boost_off()

  if (App.bass_cut_enabled) {
    App.video_bass_cut_off()
  }
  else {
    App.video_bass_cut_on()
  }
}

App.video_bass_cut_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.bass_node) {
      App.button_highlight(`video_bass_opts_cut`)
      App.bass_cut_enabled = true
      App.set_bass_gain(-8)
    }
  }
}

App.video_bass_cut_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.bass_node) {
      App.button_highlight(`video_bass_opts_cut`, false)
      App.bass_cut_enabled = false
      App.set_bass_gain(0)
    }
  }
}

App.video_treble_boost_toggle = () => {
  App.video_treble_cut_off()

  if (App.treble_boost_enabled) {
    App.video_treble_boost_off()
  }
  else {
    App.video_treble_boost_on()
  }
}

App.video_treble_boost_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.treble_node) {
      App.button_highlight(`video_treble_opts_boost`)
      App.treble_boost_enabled = true
      App.set_treble_gain(6)
    }
  }
}

App.video_treble_boost_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.treble_node) {
      App.button_highlight(`video_treble_opts_boost`, false)
      App.treble_boost_enabled = false
      App.set_treble_gain(0)
    }
  }
}

App.video_treble_cut_toggle = () => {
  App.video_treble_boost_off()

  if (App.treble_cut_enabled) {
    App.video_treble_cut_off()
  }
  else {
    App.video_treble_cut_on()
  }
}

App.video_treble_cut_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.treble_node) {
      App.button_highlight(`video_treble_opts_cut`)
      App.treble_cut_enabled = true
      App.set_treble_gain(-8)
    }
  }
}

App.video_treble_cut_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.treble_node) {
      App.button_highlight(`video_treble_opts_cut`, false)
      App.treble_cut_enabled = false
      App.set_treble_gain(0)
    }
  }
}

App.image_rotate = (direction) => {
  App.show_modal_image()
  let image = DOM.el(`#modal_image`)

  if (!image) {
    return
  }

  App.unexpand_modal_image()

  if (!image.dataset.rotation) {
    image.dataset.rotation = 0
  }

  let current_rotation = parseInt(image.dataset.rotation)

  if (direction === `clockwise`) {
    current_rotation += 90
  }
  else if (direction === `counterclockwise`) {
    current_rotation -= 90
  }

  image.dataset.rotation = current_rotation
  image.style.transform = `rotate(${current_rotation}deg)`

  App.corner_msg({
    mode: `modal_image`,
    text: `Clockwise | Counter`,
    delay: App.rotate_popup_delay,
    on_click: () => {
      App.image_rotate(`clockwise`)
    },
    on_middle_click: () => {
      App.image_rotate(`counterclockwise`)
    },
  })
}

App.reset_image_rotation = () => {
  let image = DOM.el(`#modal_image`)

  if (!image) {
    return
  }

  image.dataset.rotation = 0
  image.style.transform = `rotate(0deg)`
}

App.start_auto_video = () => {
  let video = App.get_video()

  if (!video) {
    return
  }

  App.auto_video_on = true

  if (video.paused) {
    App.auto_video_action()
  }
  else {
    App.start_auto_video_timeout()
  }

  App.button_highlight(`video_commands_opts_auto`)
}

App.stop_auto_video = () => {
  App.auto_video_on = false
  clearTimeout(App.auto_video_timeout)
  App.button_highlight(`video_commands_opts_auto`, false)
}

App.toggle_auto_video = () => {
  if (App.auto_video_on) {
    App.stop_auto_video()
  }
  else {
    App.start_auto_video()
  }
}

App.start_auto_video_timeout = () => {
  let delay_type = App.random_int({min: 1, max: 3})
  let delay

  if (delay_type === 1) {
    delay = App.random_int({min: App.SECOND * 5, max: App.SECOND * 10})
  }
  else if (delay_type === 2) {
    delay = App.random_int({min: App.SECOND * 15, max: App.SECOND * 30})
  }
  else {
    delay = App.random_int({min: App.SECOND * 45, max: App.SECOND * 60})
  }

  App.auto_video_timeout = setTimeout(() => {
    App.auto_video_action()
  }, delay)
}

App.auto_video_action = () => {
  if (App.auto_video_on) {
    App.video_jump(false)
    App.start_auto_video_timeout()
  }
}