#!/usr/bin/env ruby

require "optparse"
require "net/http"
require "uri"
require "json"
require "open3"

# Default values
url = "https://someurl.com"
username = "someusername"
password = "somepassword"
endpoint = "apiupload"
file_path = nil
compress = "off"
prompt = false

# Parse command-line options
OptionParser.new do |opts|
  opts.banner = "Usage: upload.rb [options] <file_path>"

  opts.on("--compress", "Compress the file into a zip") do
    compress = "on"
  end

  opts.on("--prompt", "Prompt for title") do
    prompt = true
  end

  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
end.parse!(into: {})

file_path = ARGV[0]

# Remove "file://" prefix if present
file_path = file_path.sub(/^file:\/\//, "") if file_path

# Convert to absolute path
file_path = File.absolute_path(file_path) if file_path

# Check required parameters
abort("Error: URL is not set") if url.nil? || url.empty?
abort("Error: USERNAME is not set") if username.nil? || username.empty?
abort("Error: PASSWORD is not set") if password.nil? || password.empty?
abort("Error: FILE_PATH is not set") if file_path.nil? || file_path.empty?

# Prompt to get the title
title = ""

if prompt
  title = `zenity --entry --title="Harambe Upload" --text="Enter a title:"`.chomp

  if $?.exitstatus != 0
    puts "User cancelled the input."
    exit 1
  end
end

puts "Uploading: #{file_path}"

# Make the POST request and capture the response
uri = URI("#{url}/#{endpoint}")
request = Net::HTTP::Post.new(uri)

form_data = [
  ["file", File.open(file_path)],
  ["title", title],
  ["username", username],
  ["password", password],
  ["compress", compress]
]

request.set_form form_data, "multipart/form-data"

response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == "https") do |http|
  http.request(request)
end

response_body = response.body

# Check if the response starts with "post/"
if response_body.start_with?("post/")
  full_url = "#{url}/#{response_body}"
  IO.popen(["xclip", "-selection", "clipboard"], "w") { |clipboard| clipboard.print full_url }
  puts "URL Copied: #{full_url}"
  system("awesome-client", 'Utils.msg("Harambe: Upload Complete")')
else
  puts response_body
end