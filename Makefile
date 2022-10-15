tag:
	git tag -d $(tag) || true
	git tag $(tag)
	git push origin -d $(tag) || true
	git push origin $(tag)

tag-delete:
	git tag -d $(tag) || true
	git push origin -d $(tag) || true
