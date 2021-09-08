from dataclasses import asdict
from datetime import datetime
import time
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage

import git

from rtofdata.config import assets_dir, data_dir, output_dir, template_dir
from rtofdata.specification.data import Specification


def get_git_data():
    repo = git.Repo(data_dir, search_parent_directories=True)
    git_version = repo.head.object.hexsha[:7]

    tagmap = {}
    for t in repo.tags:
        cmt = repo.commit(t)
        tagmap.setdefault(cmt, []).append(t)

    git_tag = tagmap.get(repo.head.object)
    if git_tag:
        git_version = str(git_tag[0])

    git_dirty = False
    if repo.is_dirty() or len(repo.untracked_files) > 0:
        git_dirty = True
        git_version = f"{git_version} (changes pending)"

    return {
        "git_version": git_version,
        "git_dirty": git_dirty,
        "git_hexsha": repo.head.object.hexsha,
        "git_msg": repo.head.object.message,
        "git_committed_date": time.strftime("%Y-%m-%d %H:%M %Z", time.gmtime(repo.head.object.committed_date)),
        "git_committer_name": repo.head.object.committer.name,
        "git_committer_email": repo.head.object.committer.email,
        "git_tags": [str(t) for t in git_tag] if git_tag else [],
        "git_tagrefs": [{
            "tag": str(t),
            "message": t.commit.message,
            "date": t.commit.committed_date,
            "comitter_name": t.commit.committer.name,
            "comitter_email": t.commit.committer.email,
        } for t in repo.tags],
    }


def create_context(spec: Specification):
    context = {
        **get_git_data(),
        "generation_time": f"{datetime.now():%d %B %Y}",
        "spec": spec,
        "record_list": spec.records,
        "records_by_flow": spec.records_by_flow,
    }

    context['field_list'] = field_list = []
    for record in spec.records:
        for field in record.fields:
            field_list.append({**asdict(field), "record": record})
    field_list.sort(key=lambda f: f"{f['record']}.{f['id']}")

    return context


def write_word_specification(spec: Specification):
    """
    Creates a detailed Word version of the specification.
    Read more about docx here: https://python-docx.readthedocs.io/en/latest/
    """

    tpl = DocxTemplate(template_dir / "template.docx")
    context = create_context(spec)
    context['milestones_image'] = InlineImage(tpl, image_descriptor=str(assets_dir / 'submission_and_collection.png'),
                                              width=Cm(16))
    context['milestones_image2'] = InlineImage(tpl, image_descriptor=str(assets_dir / 'RTOF_program_path.png'),
                                              width=Cm(16))

    context['erd_image'] = InlineImage(tpl, image_descriptor=str(output_dir / 'record-relationships.png'),
                                              width=Cm(16))



    tpl.render(context)
    tpl.save(output_dir / "specification.docx")
